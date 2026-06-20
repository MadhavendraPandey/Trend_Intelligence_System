"""Validation Core service for the friction module.

Purpose:
    Calculate evidence-backed validation metrics and generate neutral
    validation summaries for friction candidates.

Philosophy:
    The system discovers reality and presents proof. It does not recommend
    actions, estimate market size, or score opportunities. Validation
    summaries describe observable facts only.
"""

from database.repositories.friction_candidate_repository import FrictionCandidateRepository


class FrictionValidationService:
    """Service for calculating metrics and generating validation summaries."""

    def __init__(self, friction_candidate_repository):
        if not isinstance(friction_candidate_repository, FrictionCandidateRepository):
            raise TypeError("FrictionValidationService requires FrictionCandidateRepository")

        self.repository = friction_candidate_repository

    def validate_candidate(self, candidate_id):
        """Calculate metrics, generate summary, and persist to candidate."""
        metrics = self.repository.calculate_validation_metrics(candidate_id)
        summary = self.generate_summary(metrics)

        return self.repository.update_candidate(
            candidate_id,
            validation_summary=summary,
            **metrics
        )

    def validate_all_candidates(self, status=None):
        """Validate all candidates, optionally filtering by status."""
        candidates = self.repository.list_candidates(status=status, limit=1000)
        results = []
        for candidate in candidates:
            results.append(self.validate_candidate(candidate["id"]))
        return results

    def generate_summary(self, metrics):
        """Generate a concise evidence-backed neutral explanation."""
        evidence_part = f"{metrics['evidence_count']} observations"
        source_part = f"{metrics['source_count']} independent sources"
        group_part = f"{metrics['group_count']} evidence groups"

        summary = (
            f"This friction is supported by {evidence_part} across {source_part} "
            f"and appears repeatedly across {group_part}."
        )

        if metrics.get('contradiction_count', 0) > 0:
            summary += f" There are {metrics['contradiction_count']} documented contradictions or rejections."

        return summary
