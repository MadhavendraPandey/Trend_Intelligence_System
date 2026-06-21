"""Repository for source records.

Purpose:
    Own database access for registered collection origins. Sources identify
    where posts came from without embedding collection behavior in modules.

Architecture notes:
    This repository is the only application layer that should issue SQL for
    the `sources` table. Modules, engines, reports, and collectors should call
    repository methods instead of managing SQLite queries directly.

Future extension guidance:
    Add source-run helpers here or in a dedicated SourceRunRepository when
    collection metrics become a first-class workflow.
"""

from core.storage import SQLiteStorage


class SourceRepository:
    """CRUD repository for the `sources` table."""

    UPDATABLE_FIELDS = {
        "source_type",
        "name",
        "base_url",
        "owner_module",
        "is_active",
    }

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("SourceRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()

    def create_source(
        self,
        source_type,
        name,
        base_url=None,
        owner_module="shared",
        is_active=True,
    ):
        """Create a source and return the inserted row."""
        cursor = self.connection.execute(
            """
            INSERT INTO sources (
                source_type,
                name,
                base_url,
                owner_module,
                is_active
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                source_type,
                name,
                base_url,
                owner_module,
                int(bool(is_active)),
            ),
        )
        self.connection.commit()
        return self.get_source(cursor.lastrowid)

    def get_source(self, source_id):
        """Return a source by id, or None when it does not exist."""
        row = self.connection.execute(
            """
            SELECT *
            FROM sources
            WHERE id = ?
            """,
            (source_id,),
        ).fetchone()
        return self._to_dict(row)

    def update_source(self, source_id, **fields):
        """Update allowed source fields and return the updated row."""
        updates = {
            key: value
            for key, value in fields.items()
            if key in self.UPDATABLE_FIELDS
        }

        if not updates:
            return self.get_source(source_id)

        assignments = [f"{key} = ?" for key in updates]
        assignments.append("updated_at = CURRENT_TIMESTAMP")
        values = list(updates.values())
        values.append(source_id)

        self.connection.execute(
            f"""
            UPDATE sources
            SET {", ".join(assignments)}
            WHERE id = ?
            """,
            values,
        )
        self.connection.commit()
        return self.get_source(source_id)

    def list_sources(self, owner_module=None, active_only=False, limit=100, offset=0):
        """Return sources, optionally filtered by owner module and active state."""
        conditions = []
        values = []

        if owner_module is not None:
            conditions.append("owner_module = ?")
            values.append(owner_module)

        if active_only:
            conditions.append("is_active = 1")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        values.extend([limit, offset])
        rows = self.connection.execute(
            f"""
            SELECT *
            FROM sources
            {where_clause}
            ORDER BY source_type, name
            LIMIT ?
            OFFSET ?
            """,
            values,
        ).fetchall()

        return [self._to_dict(row) for row in rows]

    def count_sources(self, owner_module=None, active_only=False):
        """Return the number of sources, optionally filtered by scope."""
        conditions = []
        values = []

        if owner_module is not None:
            conditions.append("owner_module = ?")
            values.append(owner_module)

        if active_only:
            conditions.append("is_active = 1")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        row = self.connection.execute(
            f"""
            SELECT COUNT(*)
            FROM sources
            {where_clause}
            """,
            values,
        ).fetchone()

        return row[0]

    def _to_dict(self, row):
        if row is None:
            return None

        return dict(row)
