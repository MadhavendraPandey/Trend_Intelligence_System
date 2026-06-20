"""Repository for friction contradictions.

Purpose:
    Explicitly manage links between friction profiles and contradicting
    evidence items to support reality discovery.
"""

from core.storage.sqlite_storage import SQLiteStorage


class FrictionContradictionRepository:
    """CRUD repository for the `friction_profile_contradictions` table."""

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("FrictionContradictionRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()

    def add_contradiction(self, profile_id, evidence_id, reasoning=None):
        """Link an evidence item as a contradiction to a profile."""
        self.connection.execute(
            """
            INSERT OR IGNORE INTO friction_profile_contradictions (
                profile_id,
                evidence_id,
                reasoning
            )
            VALUES (?, ?, ?)
            """,
            (profile_id, evidence_id, reasoning),
        )
        self.connection.commit()

    def list_for_profile(self, profile_id):
        """Return all contradictions for a specific profile with evidence details."""
        rows = self.connection.execute(
            """
            SELECT fpc.*, e.observation, e.source_url, e.source_type, e.author
            FROM friction_profile_contradictions fpc
            JOIN evidence e ON e.evidence_id = fpc.evidence_id
            WHERE fpc.profile_id = ?
            """,
            (profile_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def count_for_profile(self, profile_id):
        """Return count of contradictions for a profile."""
        row = self.connection.execute(
            "SELECT COUNT(*) FROM friction_profile_contradictions WHERE profile_id = ?",
            (profile_id,),
        ).fetchone()
        return row[0]
