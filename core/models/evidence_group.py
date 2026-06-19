"""Evidence group models for the Intelligence Platform.

Purpose:
    Represent a named collection of related evidence records without deciding
    what the collection means. Evidence groups are organizational containers,
    not frictions, complaints, opportunities, scores, or recommendations.

Architecture notes:
    These models are storage-shaped data contracts. They contain no grouping
    algorithm, semantic similarity, embeddings, LLM logic, clustering, or
    business interpretation.

Future extension guidance:
    Future services may propose group membership, but persisted groups should
    remain evidence collections until a later approved module explicitly
    interprets them.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class EvidenceGroup:
    """A durable container for related evidence records."""

    id: Optional[int]
    title: str
    description: Optional[str] = None
    status: str = "open"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata_json: Optional[str] = None

    @classmethod
    def from_record(cls, record: Mapping[str, Any]):
        """Build an EvidenceGroup model from a repository row dictionary."""
        return cls(
            id=record.get("id"),
            title=record["title"],
            description=record.get("description"),
            status=record.get("status", "open"),
            created_at=record.get("created_at"),
            updated_at=record.get("updated_at"),
            metadata_json=record.get("metadata_json"),
        )

    def to_record(self):
        """Return a storage-shaped dictionary without adding interpretation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata_json": self.metadata_json,
        }


@dataclass(frozen=True)
class EvidenceGroupMember:
    """Membership link between one evidence group and one evidence record."""

    group_id: int
    evidence_id: int

    @classmethod
    def from_record(cls, record: Mapping[str, Any]):
        """Build an EvidenceGroupMember model from a repository row dictionary."""
        return cls(
            group_id=record["group_id"],
            evidence_id=record["evidence_id"],
        )

    def to_record(self):
        """Return a storage-shaped membership dictionary."""
        return {
            "group_id": self.group_id,
            "evidence_id": self.evidence_id,
        }
