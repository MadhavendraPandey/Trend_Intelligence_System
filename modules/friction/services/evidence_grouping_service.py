"""Evidence grouping service interfaces.

Purpose:
    Provide an interface boundary for future evidence grouping workflows
    without implementing grouping algorithms.

Architecture notes:
    This service coordinates `EvidenceGroupRepository` calls only when supplied
    explicit group and evidence identifiers by a caller. It does not perform
    clustering, semantic similarity, embeddings, LLM grouping, friction logic,
    complaint logic, opportunity detection, scoring, ranking, or extraction.

Future extension guidance:
    Future grouping strategies should subclass `BaseEvidenceGroupingService`
    or compose this service. Algorithms should propose memberships explicitly
    and keep persistence delegated to `EvidenceGroupRepository`.
"""

from abc import ABC, abstractmethod

from database.repositories.evidence_group_repository import EvidenceGroupRepository


class BaseEvidenceGroupingService(ABC):
    """Interface for explicit evidence grouping workflows."""

    def __init__(self, evidence_group_repository):
        if not isinstance(evidence_group_repository, EvidenceGroupRepository):
            raise TypeError(
                "BaseEvidenceGroupingService requires EvidenceGroupRepository"
            )

        self.evidence_group_repository = evidence_group_repository

    @abstractmethod
    def create_group(self, title, description=None, status="open", metadata_json=None):
        """Create a group from caller-supplied metadata."""

    @abstractmethod
    def add_evidence(self, group_id, evidence_id):
        """Add caller-specified evidence to a caller-specified group."""


class EvidenceGroupingService(BaseEvidenceGroupingService):
    """Minimal explicit grouping service.

    This implementation is deliberately thin. It creates groups and membership
    links only from explicit caller input; it does not decide which evidence
    belongs together.
    """

    def create_group(self, title, description=None, status="open", metadata_json=None):
        """Create a group using explicit caller-provided fields."""
        return self.evidence_group_repository.create_group(
            title=title,
            description=description,
            status=status,
            metadata_json=metadata_json,
        )

    def add_evidence(self, group_id, evidence_id):
        """Persist an explicit evidence membership link."""
        return self.evidence_group_repository.add_member(
            group_id=group_id,
            evidence_id=evidence_id,
        )
