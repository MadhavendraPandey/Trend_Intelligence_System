"""Friction service interfaces.

Purpose:
    Reserve service boundaries for future friction-related workflows. Current
    services operate on evidence grouping only and do not implement friction
    intelligence.

Architecture notes:
    Services may coordinate repositories, but they must not bypass repository
    boundaries or execute raw SQL. This package currently exposes grouping
    interfaces only.

Future extension guidance:
    Add concrete services only when their business behavior is approved. Keep
    embeddings, friction logic, and opportunity detection out until an explicit
    phase introduces them.
"""

from modules.friction.services.evidence_grouping_service import (
    BaseEvidenceGroupingService,
    EvidenceGroupingService,
)
from modules.friction.services.friction_candidate_generation_service import (
    FrictionCandidateGenerationService,
    FrictionCandidateGenerationValidationError,
)
from modules.friction.services.profile_service import FrictionProfileService
from modules.friction.services.traceability_service import TraceabilityService
from modules.friction.services.validation_service import FrictionValidationService
from modules.friction.services.evolution_service import EvolutionService
from modules.friction.services.relationship_service import RelationshipService
from modules.friction.services.contradiction_service import ContradictionService
from modules.friction.services.llm_evidence_grouping_service import (
    LLMEvidenceGroupingService,
    LLMGroupingValidationError,
)

__all__ = [
    "BaseEvidenceGroupingService",
    "EvidenceGroupingService",
    "FrictionCandidateGenerationService",
    "FrictionCandidateGenerationValidationError",
    "LLMEvidenceGroupingService",
    "LLMGroupingValidationError",
    "FrictionValidationService",
    "FrictionProfileService",
    "TraceabilityService",
    "EvolutionService",
    "RelationshipService",
    "ContradictionService",
]
