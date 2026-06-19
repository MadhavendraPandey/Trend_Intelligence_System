"""Validation event model for evidence review history.

Purpose:
    Represent a human validation action against an evidence record. Validation
    is stored as history, not as a confidence score or platform judgment.

Architecture notes:
    Validation events are scoped to evidence in Phase 6. Future phases can add
    validation events for trends, frictions, or other intelligence objects with
    separate schema changes once those objects exist.

Future extension guidance:
    Prefer adding new event actions over mutating old events when review
    workflows evolve. This preserves an auditable trail of human judgment.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class ValidationEvent:
    """Human review action associated with a single evidence record."""

    validation_event_id: Optional[int]
    evidence_id: int
    action: str
    reason: Optional[str] = None
    actor: Optional[str] = None
    created_at: Optional[str] = None

    @classmethod
    def from_record(cls, record: Mapping[str, Any]):
        """Build a ValidationEvent model from a repository row dictionary."""
        return cls(
            validation_event_id=record.get("validation_event_id"),
            evidence_id=record["evidence_id"],
            action=record["action"],
            reason=record.get("reason"),
            actor=record.get("actor"),
            created_at=record.get("created_at"),
        )

    def to_record(self):
        """Return a storage-shaped dictionary for repository persistence."""
        return {
            "validation_event_id": self.validation_event_id,
            "evidence_id": self.evidence_id,
            "action": self.action,
            "reason": self.reason,
            "actor": self.actor,
            "created_at": self.created_at,
        }
