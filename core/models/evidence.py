"""Evidence domain model for the Intelligence Platform.

Purpose:
    Represent an atomic, verifiable observation extracted from a source post.
    Evidence is the reusable platform material that future trend, friction, and
    other intelligence modules can reference.

Architecture notes:
    This model contains no scoring, ranking, confidence, trend logic, friction
    logic, extraction logic, or AI prompts. It mirrors the Phase 6 SQLite
    foundation and keeps the original observation separate from later human
    validation events.

Future extension guidance:
    Add relationships through separate module-specific join tables when trend,
    friction, or future intelligence objects are implemented. Keep evidence
    neutral and reusable rather than owned by one module.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class Evidence:
    """Atomic observation with source traceability and preserved context."""

    evidence_id: Optional[int]
    post_id: int
    evidence_type: str
    observation: str
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    captured_at: Optional[str] = None
    context: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: Optional[str] = None

    @classmethod
    def from_record(cls, record: Mapping[str, Any]):
        """Build an Evidence model from a repository row dictionary."""
        return cls(
            evidence_id=record.get("evidence_id"),
            post_id=record["post_id"],
            evidence_type=record["evidence_type"],
            observation=record["observation"],
            source_url=record.get("source_url"),
            source_type=record.get("source_type"),
            author=record.get("author"),
            published_at=record.get("published_at"),
            captured_at=record.get("captured_at"),
            context=record.get("context"),
            metadata_json=record.get("metadata_json"),
            created_at=record.get("created_at"),
        )

    def to_record(self):
        """Return a storage-shaped dictionary without adding interpretation."""
        return {
            "evidence_id": self.evidence_id,
            "post_id": self.post_id,
            "evidence_type": self.evidence_type,
            "observation": self.observation,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "author": self.author,
            "published_at": self.published_at,
            "captured_at": self.captured_at,
            "context": self.context,
            "metadata_json": self.metadata_json,
            "created_at": self.created_at,
        }
