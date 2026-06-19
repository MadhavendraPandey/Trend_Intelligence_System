"""Core model exports for platform data objects.

Purpose:
    Expose shared, module-neutral models used by the Intelligence Platform.

Architecture notes:
    Core models must not depend on trend, friction, report, collector, or
    website code. They describe durable platform concepts only.

Future extension guidance:
    Add models here as storage-backed platform objects are introduced, keeping
    module-specific behavior in module packages.
"""

from core.models.evidence import Evidence
from core.models.evidence_group import EvidenceGroup, EvidenceGroupMember
from core.models.friction_candidate import FrictionCandidate, FrictionCandidateGroup
from core.models.validation_event import ValidationEvent

__all__ = [
    "Evidence",
    "EvidenceGroup",
    "EvidenceGroupMember",
    "FrictionCandidate",
    "FrictionCandidateGroup",
    "ValidationEvent",
]
