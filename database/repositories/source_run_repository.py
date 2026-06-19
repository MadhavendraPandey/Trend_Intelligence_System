"""Repository for source run and collection stat records.

Purpose:
    Own database access for operational collection counters stored in
    `source_runs`. This replaces the previous JSON-backed collection stats
    file during the SQLite cutover.

Architecture notes:
    Collection code should continue to call the stats manager facade. The
    stats manager delegates persistence here so collectors do not execute SQL.

Future extension guidance:
    Add explicit run lifecycle methods when collectors are refactored to start
    and finish named source runs.
"""

import json

from core.storage import SQLiteStorage
from database.repositories.source_repository import SourceRepository


class SourceRunRepository:
    """Repository for source run counters."""

    METRICS = {
        "seen": "items_seen",
        "duplicates_removed": "duplicates_seen",
        "quality_removed": "quality_removed",
        "irrelevant_removed": "irrelevant_removed",
        "stored": "items_stored",
    }

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("SourceRunRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()
        self.sources = SourceRepository(storage)
        self._ensure_runtime_columns()

    def increment_stat(self, source_type, metric):
        """Increment a collection stat for a source type."""
        if metric not in self.METRICS:
            raise ValueError(f"Unknown collection stat metric: {metric}")

        run_id = self._get_or_create_current_run(source_type)
        column = self.METRICS[metric]
        self.connection.execute(
            f"""
            UPDATE source_runs
            SET {column} = {column} + 1
            WHERE id = ?
            """,
            (run_id,),
        )
        self.connection.commit()

    def get_stats(self, default_sources):
        """Return aggregate stats in the legacy stats-manager shape."""
        stats = {
            source: {
                "seen": 0,
                "duplicates_removed": 0,
                "quality_removed": 0,
                "irrelevant_removed": 0,
                "stored": 0,
            }
            for source in default_sources
        }

        rows = self.connection.execute(
            """
            SELECT
                s.source_type,
                COALESCE(SUM(sr.items_seen), 0) AS seen,
                COALESCE(SUM(sr.duplicates_seen), 0) AS duplicates_removed,
                COALESCE(SUM(sr.quality_removed), 0) AS quality_removed,
                COALESCE(SUM(sr.irrelevant_removed), 0) AS irrelevant_removed,
                COALESCE(SUM(sr.items_stored), 0) AS stored
            FROM sources s
            LEFT JOIN source_runs sr ON sr.source_id = s.id
            GROUP BY s.source_type
            ORDER BY s.source_type
            """
        ).fetchall()

        for row in rows:
            stats[row["source_type"]] = {
                "seen": row["seen"],
                "duplicates_removed": row["duplicates_removed"],
                "quality_removed": row["quality_removed"],
                "irrelevant_removed": row["irrelevant_removed"],
                "stored": row["stored"],
            }

        return stats

    def latest_run(self):
        """Return the most recent source run, or None when no runs exist."""
        row = self.connection.execute(
            """
            SELECT
                sr.*,
                s.source_type,
                s.name AS source_name
            FROM source_runs sr
            INNER JOIN sources s ON s.id = sr.source_id
            ORDER BY COALESCE(sr.finished_at, sr.started_at) DESC, sr.id DESC
            LIMIT 1
            """
        ).fetchone()
        return self._to_dict(row)

    def list_runs(self, source_id=None, status=None, limit=100, offset=0):
        """Return source runs for read-only operational inspection."""
        conditions = []
        values = []

        if source_id is not None:
            conditions.append("sr.source_id = ?")
            values.append(source_id)

        if status is not None:
            conditions.append("sr.status = ?")
            values.append(status)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        values.extend([limit, offset])
        rows = self.connection.execute(
            f"""
            SELECT
                sr.*,
                s.source_type,
                s.name AS source_name
            FROM source_runs sr
            INNER JOIN sources s ON s.id = sr.source_id
            {where_clause}
            ORDER BY COALESCE(sr.finished_at, sr.started_at) DESC, sr.id DESC
            LIMIT ?
            OFFSET ?
            """,
            values,
        ).fetchall()
        return [self._to_dict(row) for row in rows]

    def count_runs(self):
        """Return total source run count."""
        row = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM source_runs
            """
        ).fetchone()
        return row[0]

    def replace_aggregate_stats(self, stats):
        """Replace aggregate source stats with one synthetic SQLite run per source."""
        with self.connection:
            self.connection.execute("DELETE FROM source_runs")

            for source_type, source_stats in (stats or {}).items():
                source = self._get_or_create_source(source_type)
                self.connection.execute(
                    """
                    INSERT INTO source_runs (
                        source_id,
                        status,
                        items_seen,
                        duplicates_seen,
                        quality_removed,
                        irrelevant_removed,
                        items_stored,
                        metadata_json
                    )
                    VALUES (?, 'imported', ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        source["id"],
                        source_stats.get("seen", 0),
                        source_stats.get("duplicates_removed", 0),
                        source_stats.get("quality_removed", 0),
                        source_stats.get("irrelevant_removed", 0),
                        source_stats.get("stored", 0),
                        json.dumps(
                            {
                                "phase": "sqlite_cutover",
                                "source": "collection_stats.json",
                            },
                            ensure_ascii=False,
                        ),
                    ),
                )

    def _get_or_create_current_run(self, source_type):
        source = self._get_or_create_source(source_type)
        metadata = json.dumps({"phase": "sqlite_cutover"}, ensure_ascii=False)
        row = self.connection.execute(
            """
            SELECT id
            FROM source_runs
            WHERE source_id = ?
              AND status = 'active'
            ORDER BY id DESC
            LIMIT 1
            """,
            (source["id"],),
        ).fetchone()

        if row:
            return row["id"]

        cursor = self.connection.execute(
            """
            INSERT INTO source_runs (
                source_id,
                status,
                metadata_json
            )
            VALUES (?, 'active', ?)
            """,
            (source["id"], metadata),
        )
        self.connection.commit()
        return cursor.lastrowid

    def _get_or_create_source(self, source_type):
        for source in self.sources.list_sources(limit=1000):
            if source["source_type"] == source_type and source["name"] == source_type:
                return source

        return self.sources.create_source(
            source_type=source_type,
            name=source_type,
            owner_module="trend",
        )

    def _ensure_runtime_columns(self):
        existing_columns = {
            row["name"]
            for row in self.connection.execute("PRAGMA table_info(source_runs)")
        }

        for column in ("quality_removed", "irrelevant_removed"):
            if column not in existing_columns:
                self.connection.execute(
                    f"""
                    ALTER TABLE source_runs
                    ADD COLUMN {column} INTEGER NOT NULL DEFAULT 0
                    """
                )

        self.connection.commit()

    def _to_dict(self, row):
        if row is None:
            return None

        return dict(row)
