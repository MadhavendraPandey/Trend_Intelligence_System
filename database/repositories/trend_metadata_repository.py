"""Repository for Trend Snapshots and Relationships.

Purpose:
    Durable storage for inter-trend connectivity and historical states.
"""

import json
from core.storage.sqlite_storage import SQLiteStorage


class TrendMetadataRepository:
    """Handles snapshots and relationships for Trends."""

    def __init__(self, storage):
        self.connection = storage.initialize()

    def create_snapshot(self, trend_id, **metrics):
        cursor = self.connection.execute(
            """
            INSERT INTO trend_snapshots (
                trend_profile_id, trend_score, mentions,
                source_count, category_count, trend_level, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trend_id,
                metrics.get("trend_score"),
                metrics.get("mentions"),
                metrics.get("source_count"),
                metrics.get("category_count"),
                metrics.get("trend_level"),
                json.dumps(metrics.get("metadata_json", {}))
            )
        )
        self.connection.commit()
        return cursor.lastrowid

    def list_snapshots(self, trend_id, limit=100):
        rows = self.connection.execute(
            "SELECT * FROM trend_snapshots WHERE trend_profile_id = ? ORDER BY snapshot_at DESC LIMIT ?",
            (trend_id, limit)
        ).fetchall()
        return [dict(row) for row in rows]

    def create_relationship(self, from_id, to_id, rel_type, explanation=None, evidence_count=0):
        self.connection.execute(
            """
            INSERT INTO trend_relationships (
                from_trend_id, to_trend_id, relationship_type,
                explanation, supporting_evidence_count
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(from_trend_id, to_trend_id, relationship_type) DO UPDATE SET
                explanation = excluded.explanation,
                supporting_evidence_count = excluded.supporting_evidence_count
            """,
            (from_id, to_id, rel_type, explanation, evidence_count)
        )
        self.connection.commit()

    def list_relationships(self, trend_id):
        rows = self.connection.execute(
            """
            SELECT * FROM trend_relationships
            WHERE from_trend_id = ? OR to_trend_id = ?
            """,
            (trend_id, trend_id)
        ).fetchall()
        return [dict(row) for row in rows]
