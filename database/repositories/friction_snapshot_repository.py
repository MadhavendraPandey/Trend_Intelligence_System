"""Repository for friction snapshots.

Purpose:
    Provide immutable historical tracking of friction profiles for temporal
    intelligence and evolution analysis.
"""

import json
from core.storage.sqlite_storage import SQLiteStorage


class FrictionSnapshotRepository:
    """CRUD repository for the `friction_snapshots` table."""

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("FrictionSnapshotRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()

    def create_snapshot(self, profile_id, **fields):
        """Create an immutable snapshot of a friction profile."""
        cursor = self.connection.execute(
            """
            INSERT INTO friction_snapshots (
                profile_id,
                title,
                description,
                evidence_count,
                source_count,
                group_count,
                post_count,
                recurrence_count,
                contradiction_count,
                classification,
                classification_reasoning,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile_id,
                fields.get("title"),
                fields.get("description"),
                fields.get("evidence_count", 0),
                fields.get("source_count", 0),
                fields.get("group_count", 0),
                fields.get("post_count", 0),
                fields.get("recurrence_count", 0),
                fields.get("contradiction_count", 0),
                fields.get("latest_classification"),
                fields.get("latest_classification_reasoning"),
                self._json_or_text(fields.get("metadata_json")),
            ),
        )
        self.connection.commit()
        return self.get_snapshot(cursor.lastrowid)

    def get_snapshot(self, snapshot_id):
        """Return a snapshot by id."""
        row = self.connection.execute(
            "SELECT * FROM friction_snapshots WHERE id = ?", (snapshot_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_for_profile(self, profile_id, limit=100):
        """Return snapshots for a specific profile, ordered by time descending."""
        rows = self.connection.execute(
            """
            SELECT *
            FROM friction_snapshots
            WHERE profile_id = ?
            ORDER BY snapshot_at DESC
            LIMIT ?
            """,
            (profile_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]

    def _json_or_text(self, value):
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return value
