"""Repository for analyzer failure records.

Purpose:
    Preserve analyzer failure history in SQLite so runtime code no longer
    depends on `failed_articles.json`.

Architecture notes:
    This is operational storage, not intelligence logic. It does not create
    evidence, trends, complaints, frictions, or scores.

Future extension guidance:
    If analyzer failures become part of observability, split them into a
    broader pipeline run repository.
"""

import json

from core.storage import SQLiteStorage


class AnalysisFailureRepository:
    """Repository for `analysis_failures` records."""

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("AnalysisFailureRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()

    def create_failure(self, failure):
        """Insert a failure record and return it."""
        cursor = self.connection.execute(
            """
            INSERT INTO analysis_failures (
                identifier,
                title,
                source_type,
                error,
                failed_at,
                raw_json
            )
            VALUES (?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP), ?)
            """,
            (
                failure.get("identifier"),
                failure.get("title"),
                failure.get("source_type"),
                failure.get("error"),
                failure.get("failed_at"),
                json.dumps(failure, ensure_ascii=False),
            ),
        )
        self.connection.commit()
        return self.get_failure(cursor.lastrowid)

    def replace_failures(self, failures):
        """Replace analyzer failure history with the supplied records."""
        with self.connection:
            self.connection.execute("DELETE FROM analysis_failures")

            for failure in failures:
                self.connection.execute(
                    """
                    INSERT INTO analysis_failures (
                        identifier,
                        title,
                        source_type,
                        error,
                        failed_at,
                        raw_json
                    )
                    VALUES (?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP), ?)
                    """,
                    (
                        failure.get("identifier"),
                        failure.get("title"),
                        failure.get("source_type"),
                        failure.get("error"),
                        failure.get("failed_at"),
                        json.dumps(failure, ensure_ascii=False),
                    ),
                )

    def list_failures(self):
        """Return all analyzer failures in insertion order."""
        rows = self.connection.execute(
            """
            SELECT *
            FROM analysis_failures
            ORDER BY id
            """
        ).fetchall()
        return [self._to_dict(row) for row in rows]

    def get_failure(self, failure_id):
        """Return a single failure record by id."""
        row = self.connection.execute(
            """
            SELECT *
            FROM analysis_failures
            WHERE id = ?
            """,
            (failure_id,),
        ).fetchone()
        return self._to_dict(row)

    def _to_dict(self, row):
        if row is None:
            return None

        result = dict(row)

        try:
            raw = json.loads(result.get("raw_json") or "{}")
        except json.JSONDecodeError:
            raw = {}

        if raw:
            return raw

        return result
