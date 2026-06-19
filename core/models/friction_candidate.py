"""Friction candidate models.

Purpose:
    Represent generated friction hypotheses and their supporting evidence group
    links. Candidate frictions are reviewable hypotheses, not validated
    frictions, opportunities, recommendations, scores, or rankings.

Architecture notes:
    These models are storage-shaped data contracts. They do not perform market
    analysis, prioritization, revenue estimation, validation, or business
    decision-making.

Future extension guidance:
    Keep validated friction objects separate from candidates. Candidate records
    should remain traceable to evidence groups so humans can review the
    supporting material before accepting or rejecting a hypothesis.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class FrictionCandidate:
    """Generated friction hypothesis backed by evidence groups."""

    id: Optional[int]
    title: str
    description: Optional[str] = None
    status: str = "generated"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata_json: Optional[str] = None

    @classmethod
    def from_record(cls, record: Mapping[str, Any]):
        """Build a FrictionCandidate model from a repository row dictionary."""
        return cls(
            id=record.get("id"),
            title=record["title"],
            description=record.get("description"),
            status=record.get("status", "generated"),
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
class FrictionCandidateGroup:
    """Link between a friction candidate and a supporting evidence group."""

    friction_candidate_id: int
    evidence_group_id: int

    @classmethod
    def from_record(cls, record: Mapping[str, Any]):
        """Build a FrictionCandidateGroup model from a repository row dictionary."""
        return cls(
            friction_candidate_id=record["friction_candidate_id"],
            evidence_group_id=record["evidence_group_id"],
        )

    def to_record(self):
        """Return a storage-shaped candidate/group link dictionary."""
        return {
            "friction_candidate_id": self.friction_candidate_id,
            "evidence_group_id": self.evidence_group_id,
        }
