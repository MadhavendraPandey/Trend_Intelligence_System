"""Repository for evidence validation events.

Purpose:
    Own database access for human validation history stored in
    `validation_events`.

Architecture notes:
    Validation records human actions without confidence fields, certainty
    estimates, scores, or rankings. This repository does not decide whether
    evidence is true; it records review history so humans can inspect it.

Future extension guidance:
    Keep validation append-oriented. If future workflows need broader targets,
    introduce explicit schema changes instead of overloading Phase 6 evidence
    validation columns.
"""

from core.storage import SQLiteStorage


class ValidationRepository:
    """CRUD repository for the `validation_events` table."""

    ALLOWED_ACTIONS = {
        "validated",
        "rejected",
        "merged",
        "reopened",
        "needs_review",
    }

    CURATION_FIELDS = {
        "reason",
        "actor",
    }

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("ValidationRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()

    def create_validation_event(
        self,
        evidence_id,
        action,
        reason=None,
        actor=None,
    ):
        """Create a validation event and return the inserted row."""
        self._validate_action(action)
        cursor = self.connection.execute(
            """
            INSERT INTO validation_events (
                evidence_id,
                action,
                reason,
                actor
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                evidence_id,
                action,
                reason,
                actor,
            ),
        )
        self.connection.commit()
        return self.get_validation_event(cursor.lastrowid)

    def get_validation_event(self, validation_event_id):
        """Return a validation event by id, or None when it does not exist."""
        row = self.connection.execute(
            """
            SELECT *
            FROM validation_events
            WHERE validation_event_id = ?
            """,
            (validation_event_id,),
        ).fetchone()
        return self._to_dict(row)

    def update_validation_event(self, validation_event_id, **fields):
        """Update review notes without changing the recorded action."""
        updates = {
            key: value
            for key, value in fields.items()
            if key in self.CURATION_FIELDS
        }

        if not updates:
            return self.get_validation_event(validation_event_id)

        assignments = [f"{key} = ?" for key in updates]
        values = list(updates.values())
        values.append(validation_event_id)

        self.connection.execute(
            f"""
            UPDATE validation_events
            SET {", ".join(assignments)}
            WHERE validation_event_id = ?
            """,
            values,
        )
        self.connection.commit()
        return self.get_validation_event(validation_event_id)

    def delete_validation_event(self, validation_event_id):
        """Delete a validation event."""
        cursor = self.connection.execute(
            """
            DELETE FROM validation_events
            WHERE validation_event_id = ?
            """,
            (validation_event_id,),
        )
        self.connection.commit()
        return cursor.rowcount

    def list_for_evidence(self, evidence_id, limit=100, offset=0):
        """Return validation history for an evidence record."""
        rows = self.connection.execute(
            """
            SELECT *
            FROM validation_events
            WHERE evidence_id = ?
            ORDER BY created_at DESC, validation_event_id DESC
            LIMIT ?
            OFFSET ?
            """,
            (evidence_id, limit, offset),
        ).fetchall()
        return [self._to_dict(row) for row in rows]

    def _validate_action(self, action):
        if action not in self.ALLOWED_ACTIONS:
            raise ValueError(f"Unsupported validation action: {action}")

    def _to_dict(self, row):
        if row is None:
            return None

        return dict(row)
