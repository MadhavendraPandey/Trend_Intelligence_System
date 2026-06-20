"""Repository for persistent friction profiles.

Purpose:
    Own database access for `friction_profiles`. Profiles are durable
    intelligence objects that aggregate validation data from candidates.

Architecture notes:
    This repository persists profiles only. It does not perform validation,
    generate summaries, or build traceability chains.

Future extension guidance:
    Add search and filtering methods as the number of profiles grows.
"""

import json
from core.storage import SQLiteStorage


class FrictionProfileRepository:
    """CRUD repository for the `friction_profiles` table."""

    ALLOWED_STATUSES = {"active", "archived"}
    UPDATABLE_FIELDS = {
        "candidate_friction_id",
        "title",
        "description",
        "validation_summary",
        "evidence_count",
        "source_count",
        "group_count",
        "post_count",
        "recurrence_count",
        "contradiction_count",
        "status",
        "metadata_json",
    }

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("FrictionProfileRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()

    def create_profile(
        self,
        title,
        candidate_friction_id=None,
        description=None,
        validation_summary=None,
        evidence_count=0,
        source_count=0,
        group_count=0,
        post_count=0,
        recurrence_count=0,
        contradiction_count=0,
        status="active",
        metadata_json=None,
    ):
        """Create a friction profile and return the inserted row."""
        self._validate_status(status)
        cursor = self.connection.execute(
            """
            INSERT INTO friction_profiles (
                candidate_friction_id,
                title,
                description,
                validation_summary,
                evidence_count,
                source_count,
                group_count,
                post_count,
                recurrence_count,
                contradiction_count,
                status,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate_friction_id,
                title,
                description,
                validation_summary,
                evidence_count,
                source_count,
                group_count,
                post_count,
                recurrence_count,
                contradiction_count,
                status,
                self._json_or_text(metadata_json),
            ),
        )
        self.connection.commit()
        return self.get_profile(cursor.lastrowid)

    def get_profile(self, profile_id):
        """Return a friction profile by id, or None when it does not exist."""
        row = self.connection.execute(
            """
            SELECT *
            FROM friction_profiles
            WHERE id = ?
            """,
            (profile_id,),
        ).fetchone()
        return self._to_dict(row)

    def get_profile_by_candidate(self, candidate_id):
        """Return a friction profile by its candidate id, or None."""
        row = self.connection.execute(
            """
            SELECT *
            FROM friction_profiles
            WHERE candidate_friction_id = ?
            """,
            (candidate_id,),
        ).fetchone()
        return self._to_dict(row)

    def update_profile(self, profile_id, **fields):
        """Update allowed profile fields and return the updated row."""
        if "status" in fields:
            self._validate_status(fields["status"])

        updates = {
            key: self._json_or_text(value)
            for key, value in fields.items()
            if key in self.UPDATABLE_FIELDS
        }

        if not updates:
            return self.get_profile(profile_id)

        assignments = [f"{key} = ?" for key in updates]
        assignments.append("updated_at = CURRENT_TIMESTAMP")
        values = list(updates.values())
        values.append(profile_id)

        self.connection.execute(
            f"""
            UPDATE friction_profiles
            SET {", ".join(assignments)}
            WHERE id = ?
            """,
            values,
        )
        self.connection.commit()
        return self.get_profile(profile_id)

    def list_profiles(self, status=None, limit=100, offset=0):
        """Return friction profiles, optionally filtered by status."""
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
            FROM friction_profiles
            {where_clause}
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
            OFFSET ?
            """,
            values,
        ).fetchall()
        return [self._to_dict(row) for row in rows]

    def count_profiles(self, status=None):
        """Return the total number of friction profiles."""
        conditions = []
        values = []

        if status is not None:
            self._validate_status(status)
            conditions.append("status = ?")
            values.append(status)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        row = self.connection.execute(
            f"""
            SELECT COUNT(*)
            FROM friction_profiles
            {where_clause}
            """,
            values,
        ).fetchone()
        return row[0]

    def _validate_status(self, status):
        if status not in self.ALLOWED_STATUSES:
            raise ValueError(f"Unsupported friction profile status: {status}")

    def _json_or_text(self, value):
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)

        return value

    def _to_dict(self, row):
        if row is None:
            return None

        return dict(row)
