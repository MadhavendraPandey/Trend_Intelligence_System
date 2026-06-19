"""Repository for evidence groups and membership links.

Purpose:
    Own database access for `evidence_groups` and `evidence_group_members`.
    Groups store collections of related evidence without adding business
    interpretation.

Architecture notes:
    This repository contains persistence operations only. It does not perform
    grouping algorithms, semantic similarity, embeddings, LLM grouping,
    friction logic, complaint logic, opportunity detection, scoring, ranking,
    or recommendations.

Future extension guidance:
    Add read methods around evidence relationships as approved workflows need
    them. Keep algorithmic grouping proposals in services that call this
    repository rather than embedding algorithms in persistence code.
"""

import json

from core.storage import SQLiteStorage


class EvidenceGroupRepository:
    """CRUD repository for evidence groups and membership links."""

    UPDATABLE_FIELDS = {
        "title",
        "description",
        "status",
        "metadata_json",
    }

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("EvidenceGroupRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()

    def create_group(
        self,
        title,
        description=None,
        status="open",
        metadata_json=None,
    ):
        """Create an evidence group and return the inserted row."""
        cursor = self.connection.execute(
            """
            INSERT INTO evidence_groups (
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
        return self.get_group(cursor.lastrowid)

    def get_group(self, group_id):
        """Return an evidence group by id, or None when it does not exist."""
        row = self.connection.execute(
            """
            SELECT *
            FROM evidence_groups
            WHERE id = ?
            """,
            (group_id,),
        ).fetchone()
        return self._to_dict(row)

    def update_group(self, group_id, **fields):
        """Update allowed group curation fields and return the updated row."""
        updates = {
            key: self._json_or_text(value)
            for key, value in fields.items()
            if key in self.UPDATABLE_FIELDS
        }

        if not updates:
            return self.get_group(group_id)

        assignments = [f"{key} = ?" for key in updates]
        assignments.append("updated_at = CURRENT_TIMESTAMP")
        values = list(updates.values())
        values.append(group_id)

        self.connection.execute(
            f"""
            UPDATE evidence_groups
            SET {", ".join(assignments)}
            WHERE id = ?
            """,
            values,
        )
        self.connection.commit()
        return self.get_group(group_id)

    def delete_group(self, group_id):
        """Delete an evidence group and cascade membership links."""
        cursor = self.connection.execute(
            """
            DELETE FROM evidence_groups
            WHERE id = ?
            """,
            (group_id,),
        )
        self.connection.commit()
        return cursor.rowcount

    def list_groups(self, status=None, limit=100, offset=0):
        """Return evidence groups, optionally filtered by status."""
        conditions = []
        values = []

        if status is not None:
            conditions.append("status = ?")
            values.append(status)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        values.extend([limit, offset])
        rows = self.connection.execute(
            f"""
            SELECT *
            FROM evidence_groups
            {where_clause}
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
            OFFSET ?
            """,
            values,
        ).fetchall()
        return [self._to_dict(row) for row in rows]

    def add_member(self, group_id, evidence_id):
        """Add an evidence record to a group and return the membership link."""
        self.connection.execute(
            """
            INSERT OR IGNORE INTO evidence_group_members (
                group_id,
                evidence_id
            )
            VALUES (?, ?)
            """,
            (group_id, evidence_id),
        )
        self.connection.commit()
        return self.get_member(group_id, evidence_id)

    def get_member(self, group_id, evidence_id):
        """Return a membership link, or None when it does not exist."""
        row = self.connection.execute(
            """
            SELECT *
            FROM evidence_group_members
            WHERE group_id = ?
              AND evidence_id = ?
            """,
            (group_id, evidence_id),
        ).fetchone()
        return self._to_dict(row)

    def remove_member(self, group_id, evidence_id):
        """Remove an evidence record from a group."""
        cursor = self.connection.execute(
            """
            DELETE FROM evidence_group_members
            WHERE group_id = ?
              AND evidence_id = ?
            """,
            (group_id, evidence_id),
        )
        self.connection.commit()
        return cursor.rowcount

    def list_members(self, group_id, limit=100, offset=0):
        """Return membership links for a group."""
        rows = self.connection.execute(
            """
            SELECT *
            FROM evidence_group_members
            WHERE group_id = ?
            ORDER BY evidence_id
            LIMIT ?
            OFFSET ?
            """,
            (group_id, limit, offset),
        ).fetchall()
        return [self._to_dict(row) for row in rows]

    def list_groups_for_evidence(self, evidence_id, limit=100, offset=0):
        """Return groups that contain an evidence record."""
        rows = self.connection.execute(
            """
            SELECT eg.*
            FROM evidence_groups eg
            INNER JOIN evidence_group_members egm
                ON egm.group_id = eg.id
            WHERE egm.evidence_id = ?
            ORDER BY eg.updated_at DESC, eg.id DESC
            LIMIT ?
            OFFSET ?
            """,
            (evidence_id, limit, offset),
        ).fetchall()
        return [self._to_dict(row) for row in rows]

    def count_groups(self):
        """Return the total number of evidence groups."""
        row = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM evidence_groups
            """
        ).fetchone()
        return row[0]

    def count_members(self, group_id=None):
        """Return membership count globally or for one group."""
        if group_id is None:
            row = self.connection.execute(
                """
                SELECT COUNT(*)
                FROM evidence_group_members
                """
            ).fetchone()
        else:
            row = self.connection.execute(
                """
                SELECT COUNT(*)
                FROM evidence_group_members
                WHERE group_id = ?
                """,
                (group_id,),
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
