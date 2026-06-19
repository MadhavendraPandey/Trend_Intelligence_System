"""Repository for friction candidates and supporting evidence group links.

Purpose:
    Own database access for generated friction hypotheses stored in
    `friction_candidates` and their traceability links in
    `friction_candidate_groups`.

Architecture notes:
    This repository persists hypotheses only. It does not validate frictions,
    detect opportunities, perform market analysis, estimate revenue, score,
    rank, prioritize, or recommend business actions.

Future extension guidance:
    Keep validated frictions in a separate future repository. Candidate records
    should remain traceable to evidence groups through explicit membership
    links.
"""

import json

from core.storage import SQLiteStorage


class FrictionCandidateRepository:
    """CRUD repository for friction candidates and evidence group links."""

    ALLOWED_STATUSES = {
        "generated",
        "reviewed",
        "accepted",
        "rejected",
    }
    UPDATABLE_FIELDS = {
        "title",
        "description",
        "status",
        "metadata_json",
    }

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("FrictionCandidateRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()

    def create_candidate(
        self,
        title,
        description=None,
        status="generated",
        metadata_json=None,
    ):
        """Create a friction candidate and return the inserted row."""
        self._validate_status(status)
        cursor = self.connection.execute(
            """
            INSERT INTO friction_candidates (
                title,
                description,
                status,
                metadata_json
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                title,
                description,
                status,
                self._json_or_text(metadata_json),
            ),
        )
        self.connection.commit()
        return self.get_candidate(cursor.lastrowid)

    def get_candidate(self, candidate_id):
        """Return a friction candidate by id, or None when it does not exist."""
        row = self.connection.execute(
            """
            SELECT *
            FROM friction_candidates
            WHERE id = ?
            """,
            (candidate_id,),
        ).fetchone()
        return self._to_dict(row)

    def update_candidate(self, candidate_id, **fields):
        """Update allowed candidate fields and return the updated row."""
        if "status" in fields:
            self._validate_status(fields["status"])

        updates = {
            key: self._json_or_text(value)
            for key, value in fields.items()
            if key in self.UPDATABLE_FIELDS
        }

        if not updates:
            return self.get_candidate(candidate_id)

        assignments = [f"{key} = ?" for key in updates]
        assignments.append("updated_at = CURRENT_TIMESTAMP")
        values = list(updates.values())
        values.append(candidate_id)

        self.connection.execute(
            f"""
            UPDATE friction_candidates
            SET {", ".join(assignments)}
            WHERE id = ?
            """,
            values,
        )
        self.connection.commit()
        return self.get_candidate(candidate_id)

    def delete_candidate(self, candidate_id):
        """Delete a friction candidate and cascade group links."""
        cursor = self.connection.execute(
            """
            DELETE FROM friction_candidates
            WHERE id = ?
            """,
            (candidate_id,),
        )
        self.connection.commit()
        return cursor.rowcount

    def list_candidates(self, status=None, limit=100, offset=0):
        """Return candidates, optionally filtered by status."""
        conditions = []
        values = []

        if status is not None:
            self._validate_status(status)
            conditions.append("status = ?")
            values.append(status)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        values.extend([limit, offset])
        rows = self.connection.execute(
            f"""
            SELECT *
            FROM friction_candidates
            {where_clause}
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
            OFFSET ?
            """,
            values,
        ).fetchall()
        return [self._to_dict(row) for row in rows]

    def add_group(self, candidate_id, evidence_group_id):
        """Link a candidate to a supporting evidence group."""
        self.connection.execute(
            """
            INSERT OR IGNORE INTO friction_candidate_groups (
                friction_candidate_id,
                evidence_group_id
            )
            VALUES (?, ?)
            """,
            (candidate_id, evidence_group_id),
        )
        self.connection.commit()
        return self.get_group_link(candidate_id, evidence_group_id)

    def get_group_link(self, candidate_id, evidence_group_id):
        """Return a candidate/group link, or None when it does not exist."""
        row = self.connection.execute(
            """
            SELECT *
            FROM friction_candidate_groups
            WHERE friction_candidate_id = ?
              AND evidence_group_id = ?
            """,
            (candidate_id, evidence_group_id),
        ).fetchone()
        return self._to_dict(row)

    def remove_group(self, candidate_id, evidence_group_id):
        """Remove a supporting evidence group link."""
        cursor = self.connection.execute(
            """
            DELETE FROM friction_candidate_groups
            WHERE friction_candidate_id = ?
              AND evidence_group_id = ?
            """,
            (candidate_id, evidence_group_id),
        )
        self.connection.commit()
        return cursor.rowcount

    def list_groups(self, candidate_id, limit=100, offset=0):
        """Return supporting group links for a candidate."""
        rows = self.connection.execute(
            """
            SELECT *
            FROM friction_candidate_groups
            WHERE friction_candidate_id = ?
            ORDER BY evidence_group_id
            LIMIT ?
            OFFSET ?
            """,
            (candidate_id, limit, offset),
        ).fetchall()
        return [self._to_dict(row) for row in rows]

    def list_candidates_for_group(self, evidence_group_id, limit=100, offset=0):
        """Return candidates supported by an evidence group."""
        rows = self.connection.execute(
            """
            SELECT fc.*
            FROM friction_candidates fc
            INNER JOIN friction_candidate_groups fcg
                ON fcg.friction_candidate_id = fc.id
            WHERE fcg.evidence_group_id = ?
            ORDER BY fc.updated_at DESC, fc.id DESC
            LIMIT ?
            OFFSET ?
            """,
            (evidence_group_id, limit, offset),
        ).fetchall()
        return [self._to_dict(row) for row in rows]

    def count_candidates(self):
        """Return the total number of friction candidates."""
        row = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM friction_candidates
            """
        ).fetchone()
        return row[0]

    def count_group_links(self, candidate_id=None):
        """Return group link count globally or for one candidate."""
        if candidate_id is None:
            row = self.connection.execute(
                """
                SELECT COUNT(*)
                FROM friction_candidate_groups
                """
            ).fetchone()
        else:
            row = self.connection.execute(
                """
                SELECT COUNT(*)
                FROM friction_candidate_groups
                WHERE friction_candidate_id = ?
                """,
                (candidate_id,),
            ).fetchone()

        return row[0]

    def _validate_status(self, status):
        if status not in self.ALLOWED_STATUSES:
            raise ValueError(f"Unsupported friction candidate status: {status}")

    def _json_or_text(self, value):
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)

        return value

    def _to_dict(self, row):
        if row is None:
            return None

        return dict(row)
