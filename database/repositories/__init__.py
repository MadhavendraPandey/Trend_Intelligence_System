"""Repository boundary for database access.

Purpose:
    Reserve a package for repository classes such as PostRepository,
    SourceRepository, and future evidence/trend/friction repositories.

Architecture notes:
    Repositories own database access patterns. Modules, engines, and reports
    should call repositories rather than executing raw SQL or managing SQLite
    connections.

Future extension guidance:
    Add new repositories here as Phase 3+ tables are introduced.
"""

from database.repositories.post_repository import PostRepository
from database.repositories.analysis_failure_repository import AnalysisFailureRepository
from database.repositories.evidence_group_repository import EvidenceGroupRepository
from database.repositories.evidence_repository import EvidenceRepository
from database.repositories.friction_candidate_repository import (
    FrictionCandidateRepository,
)
from database.repositories.friction_profile_repository import FrictionProfileRepository
from database.repositories.friction_snapshot_repository import FrictionSnapshotRepository
from database.repositories.friction_relationship_repository import FrictionRelationshipRepository
from database.repositories.friction_contradiction_repository import FrictionContradictionRepository
from database.repositories.source_run_repository import SourceRunRepository
from database.repositories.source_repository import SourceRepository
from database.repositories.operator_repository import OperatorRepository
from database.repositories.trend_profile_repository import TrendProfileRepository
from database.repositories.trend_metadata_repository import TrendMetadataRepository
from database.repositories.validation_repository import ValidationRepository

__all__ = [
    "AnalysisFailureRepository",
    "EvidenceGroupRepository",
    "EvidenceRepository",
    "FrictionCandidateRepository",
    "FrictionProfileRepository",
    "FrictionSnapshotRepository",
    "FrictionRelationshipRepository",
    "FrictionContradictionRepository",
    "OperatorRepository",
    "TrendProfileRepository",
    "TrendMetadataRepository",
    "PostRepository",
    "SourceRunRepository",
    "SourceRepository",
    "ValidationRepository",
]
