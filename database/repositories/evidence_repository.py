"""Repository for first-class evidence records.

Purpose:
    Own database access for atomic, verifiable observations stored in the
    `evidence` table.

Architecture notes:
    Evidence is neutral platform infrastructure. This repository does not
    extract evidence, score evidence, group evidence, create trends, create
    frictions, or invoke AI. It persists observations and returns row-shaped
    dictionaries for callers that need durable traceability.

Future extension guidance:
    Add module-specific evidence links in future repositories or join-table
    repositories. Keep the evidence record itself reusable across modules.
"""

import json

from core.storage import SQLiteStorage


class EvidenceRepository:
    """CRUD repository for the `evidence` table."""

    CURATION_FIELDS = {
        "context",
        "metadata_json",
    }

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("EvidenceRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()

    def create_evidence(
        self,
        post_id,
        evidence_type,
        observation,
        source_url=None,
        source_type=None,
        author=None,
        published_at=None,
        captured_at=None,
        context=None,
        metadata_json=None,
    ):
        """Create an evidence record and return the inserted row."""
        cursor = self.connection.execute(
            """
            INSERT INTO evidence (
                post_id,
                evidence_type,
                observation,
                source_url,
                source_type,
                author,
                published_at,
                captured_at,
                context,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP), ?, ?)
            """,
            (
                post_id,
                evidence_type,
                observation,
                source_url,
                source_type,
                author,
                published_at,
                captured_at,
                context,
                self._json_or_text(metadata_json),
            ),
        )
        self.connection.commit()
        return self.get_evidence(cursor.lastrowid)

    def get_evidence(self, evidence_id):
        """Return an evidence record by id, or None when it does not exist."""
        row = self.connection.execute(
            """
            SELECT *
            FROM evidence
            WHERE evidence_id = ?
            """,
            (evidence_id,),
        ).fetchone()
        return self._to_dict(row)

    def update_evidence(self, evidence_id, **fields):
        """Update curation fields without changing the original observation."""
        updates = {
            key: self._json_or_text(value)
            for key, value in fields.items()
            if key in self.CURATION_FIELDS
        }

        if not updates:
            return self.get_evidence(evidence_id)

        assignments = [f"{key} = ?" for key in updates]
        values = list(updates.values())
        values.append(evidence_id)

        self.connection.execute(
            f"""
            UPDATE evidence
            SET {", ".join(assignments)}
            WHERE evidence_id = ?
            """,
            values,
        )
        self.connection.commit()
        return self.get_evidence(evidence_id)

    def delete_evidence(self, evidence_id):
        """Delete an evidence record and cascade its validation events."""
        cursor = self.connection.execute(
            """
            DELETE FROM evidence
            WHERE evidence_id = ?
            """,
            (evidence_id,),
        )
        self.connection.commit()
        return cursor.rowcount

    def list_evidence(self, post_id=None, evidence_type=None, limit=100, offset=0):
        """Return evidence records, optionally filtered by post or type."""
        conditions = []
        values = []

        if post_id is not None:
            conditions.append("post_id = ?")
            values.append(post_id)

        if evidence_type is not None:
            conditions.append("evidence_type = ?")
            values.append(evidence_type)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        values.extend([limit, offset])
        rows = self.connection.execute(
            f"""
            SELECT *
            FROM evidence
            {where_clause}
            ORDER BY captured_at DESC, evidence_id DESC
            LIMIT ?
            OFFSET ?
            """,
            values,
        ).fetchall()
        return [self._to_dict(row) for row in rows]

    def list_by_post(self, post_id, limit=100, offset=0):
        """Return evidence records associated with a post."""
        return self.list_evidence(post_id=post_id, limit=limit, offset=offset)

    def count_evidence(self):
        """Return the total number of evidence records."""
        row = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM evidence
            """
        ).fetchone()
        return row[0]

    def _json_or_text(self, value):
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)

        return value

    def _to_dict(self, row):
        if row is None:
            return None

        return dict(row)
