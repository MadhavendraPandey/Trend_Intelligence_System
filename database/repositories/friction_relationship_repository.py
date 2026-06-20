"""Repository for inter-friction relationships.

Purpose:
    Manage the mapping of connections between different friction profiles
    to build a navigable reality graph.
"""

import json
from core.storage.sqlite_storage import SQLiteStorage


class FrictionRelationshipRepository:
    """CRUD repository for the `friction_relationships` table."""

    ALLOWED_TYPES = {
        "related",
        "overlapping",
        "dependent",
        "competing",
        "causal_candidate",
    }

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("FrictionRelationshipRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()

    def create_relationship(self, from_id, to_id, rel_type, explanation=None, **metrics):
        """Create or update a relationship between two profiles."""
        if rel_type not in self.ALLOWED_TYPES:
            raise ValueError(f"Unsupported relationship type: {rel_type}")

        self.connection.execute(
            """
            INSERT INTO friction_relationships (
                from_profile_id,
                to_profile_id,
                relationship_type,
                explanation,
                supporting_evidence_count,
                supporting_source_count
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(from_profile_id, to_profile_id, relationship_type) DO UPDATE SET
                explanation = excluded.explanation,
                supporting_evidence_count = excluded.supporting_evidence_count,
                supporting_source_count = excluded.supporting_source_count,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                from_id,
                to_id,
                rel_type,
                explanation,
                metrics.get("supporting_evidence_count", 0),
                metrics.get("supporting_source_count", 0),
            ),
        )
        self.connection.commit()
        return self.get_relationship(from_id, to_id, rel_type)

    def get_relationship(self, from_id, to_id, rel_type):
        """Return a specific relationship."""
        row = self.connection.execute(
            """
            SELECT * FROM friction_relationships
            WHERE from_profile_id = ? AND to_profile_id = ? AND relationship_type = ?
            """,
            (from_id, to_id, rel_type),
        ).fetchone()
        return dict(row) if row else None

    def list_for_profile(self, profile_id):
        """Return all relationships where the profile is either source or target."""
        rows = self.connection.execute(
            """
            SELECT * FROM friction_relationships
            WHERE from_profile_id = ? OR to_profile_id = ?
            ORDER BY supporting_evidence_count DESC
            """,
            (profile_id, profile_id),
        ).fetchall()
        return [dict(row) for row in rows]

    def list_all(self, limit=500):
        """Return all relationships in the system."""
        rows = self.connection.execute(
            "SELECT * FROM friction_relationships LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
