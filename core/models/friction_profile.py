"""Friction Profile domain models.

Purpose:
    Represent durable, persistent friction identities that aggregate
    validated candidate data. Friction Profiles are the primary intelligence
    objects of the platform.

Architecture notes:
    These models are storage-shaped data contracts. They do not perform
    validation, generation, or build traceability chains.

Future extension guidance:
    Keep profiles independent from transient pipeline execution.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class FrictionProfile:
    """Durable friction identity backed by validated candidates."""

    id: Optional[int]
    candidate_friction_id: Optional[int]
    title: str
    description: Optional[str] = None
    validation_summary: Optional[str] = None
    evidence_count: int = 0
    source_count: int = 0
    group_count: int = 0
    post_count: int = 0
    recurrence_count: int = 0
    contradiction_count: int = 0
    status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata_json: Optional[str] = None

    @classmethod
    def from_record(cls, record: Mapping[str, Any]):
        """Build a FrictionProfile model from a repository row dictionary."""
        return cls(
            id=record.get("id"),
            candidate_friction_id=record.get("candidate_friction_id"),
            title=record["title"],
            description=record.get("description"),
            validation_summary=record.get("validation_summary"),
            evidence_count=record.get("evidence_count", 0),
            source_count=record.get("source_count", 0),
            group_count=record.get("group_count", 0),
            post_count=record.get("post_count", 0),
            recurrence_count=record.get("recurrence_count", 0),
            contradiction_count=record.get("contradiction_count", 0),
            status=record.get("status", "active"),
            created_at=record.get("created_at"),
            updated_at=record.get("updated_at"),
            metadata_json=record.get("metadata_json"),
        )

    def to_record(self):
        """Return a storage-shaped dictionary without adding interpretation."""
        return {
            "id": self.id,
            "candidate_friction_id": self.candidate_friction_id,
            "title": self.title,
            "description": self.description,
            "validation_summary": self.validation_summary,
            "evidence_count": self.evidence_count,
            "source_count": self.source_count,
            "group_count": self.group_count,
            "post_count": self.post_count,
            "recurrence_count": self.recurrence_count,
            "contradiction_count": self.contradiction_count,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata_json": self.metadata_json,
        }
