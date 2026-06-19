"""Friction evidence extractor interfaces and implementations.

Purpose:
    Reserve the friction extractor package for evidence extraction
    infrastructure. This package contains rule-based and LLM-backed
    Post -> Evidence extractors only. It does not implement friction
    intelligence, complaint extraction, candidate generation, clustering,
    validation, or reports.

Architecture notes:
    Extractors read posts through `PostRepository` and persist observations
    through `EvidenceRepository`. They should not execute SQL directly.

Future extension guidance:
    Add concrete extractors here when extraction rules or model strategies are
    explicitly approved. Those implementations should return neutral evidence
    records before any complaint or friction workflow is introduced.
"""

from modules.friction.extractors.evidence_extractor import (
    BaseEvidenceExtractor,
    EvidenceDraft,
    EvidenceExtractor,
)
from modules.friction.extractors.llm_evidence_extractor import (
    LLMEvidenceExtractor,
    LLMResponseValidationError,
)

__all__ = [
    "BaseEvidenceExtractor",
    "EvidenceDraft",
    "EvidenceExtractor",
    "LLMEvidenceExtractor",
    "LLMResponseValidationError",
]
