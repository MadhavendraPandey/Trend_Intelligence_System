"""Repository for Trend Profiles and intelligence objects.

Purpose:
    Durable storage and retrieval of trends discovered in the pipeline.
"""

import json
from core.storage.sqlite_storage import SQLiteStorage


class TrendProfileRepository:
    """CRUD repository for the `trend_profiles` table."""

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("TrendProfileRepository requires SQLiteStorage")
        self.storage = storage
        self.connection = storage.initialize()

    def create_or_update_trend(self, title, **fields):
        """Idempotent creation or update of a trend profile."""
        existing = self.get_by_title(title)

        if existing:
            return self.update_trend(existing["id"], **fields)

        cursor = self.connection.execute(
            """
            INSERT INTO trend_profiles (
                title, summary, description, domain, theme,
                trend_score, trend_level, confidence, mentions,
                source_count, category_count, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                fields.get("summary"),
                fields.get("description"),
                fields.get("domain"),
                fields.get("theme"),
                fields.get("trend_score", 0.0),
                fields.get("trend_level"),
                fields.get("confidence"),
                fields.get("mentions", 0),
                fields.get("source_count", 0),
                fields.get("category_count", 0),
                json.dumps(fields.get("metadata_json", {}))
            ),
        )
        self.connection.commit()
        return self.get_trend(cursor.lastrowid)

    def get_trend(self, trend_id):
        row = self.connection.execute(
            "SELECT * FROM trend_profiles WHERE id = ?", (trend_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_by_title(self, title):
        row = self.connection.execute(
            "SELECT * FROM trend_profiles WHERE title = ?", (title,)
        ).fetchone()
        return dict(row) if row else None

    def update_trend(self, trend_id, **fields):
        allowed = {
            "summary", "description", "domain", "theme",
            "trend_score", "trend_level", "confidence", "mentions",
            "source_count", "category_count", "metadata_json"
        }
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get_trend(trend_id)

        if "metadata_json" in updates:
            updates["metadata_json"] = json.dumps(updates["metadata_json"])

        assignments = [f"{k} = ?" for k in updates]
        assignments.append("updated_at = CURRENT_TIMESTAMP")
        values = list(updates.values())
        values.append(trend_id)

        self.connection.execute(
            f"UPDATE trend_profiles SET {', '.join(assignments)} WHERE id = ?",
            values
        )
        self.connection.commit()
        return self.get_trend(trend_id)

    def list_trends(self, limit=100, offset=0, domain=None):
        where = ""
        values = []
        if domain:
            where = "WHERE domain = ?"
            values.append(domain)

        values.extend([limit, offset])
        rows = self.connection.execute(
            f"SELECT * FROM trend_profiles {where} ORDER BY trend_score DESC LIMIT ? OFFSET ?",
            values
        ).fetchall()
        return [dict(row) for row in rows]

    def count_trends(self):
        return self.connection.execute("SELECT COUNT(*) FROM trend_profiles").fetchone()[0]

    def add_evidence(self, trend_id, evidence_id):
        self.connection.execute(
            "INSERT OR IGNORE INTO trend_evidence (trend_profile_id, evidence_id) VALUES (?, ?)",
            (trend_id, evidence_id)
        )
        self.connection.commit()

    def list_evidence_for_trend(self, trend_id):
        rows = self.connection.execute(
            """
            SELECT e.* FROM evidence e
            JOIN trend_evidence te ON te.evidence_id = e.evidence_id
            WHERE te.trend_profile_id = ?
            ORDER BY e.captured_at DESC
            """,
            (trend_id,)
        ).fetchall()
        return [dict(row) for row in rows]
