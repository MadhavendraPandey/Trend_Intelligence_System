"""Contradiction Intelligence service.

Purpose:
    Surface evidence that specifically contradicts the core claim of a
    friction profile.
    Calculate contradiction metrics and manage contradiction links.

Philosophy:
    Transparency is prioritized over confidence. Contradictions must never
    be hidden.
"""

class ContradictionService:
    """Service for managing contradiction intelligence."""

    def __init__(
        self,
        contradiction_repository,
        profile_repository,
        candidate_repository,
        evidence_repository
    ):
        self.contra_repo = contradiction_repository
        self.profile_repo = profile_repository
        self.candidate_repo = candidate_repository
        self.evidence_repo = evidence_repository

    def sync_contradictions_for_profile(self, profile_id):
        """Identify and link contradicting evidence from the candidate's chain."""
        profile = self.profile_repo.get_profile(profile_id)
        if not profile or not profile.get("candidate_friction_id"):
            return 0

        # Get 'rejected' validation events for evidence linked to the candidate
        candidate_id = profile["candidate_friction_id"]

        # We can find these via the repository or direct query
        # For simplicity, we use the candidate_repository's logic or expand it
        metrics = self.candidate_repo.calculate_validation_metrics(candidate_id)

        # If we have contradictions, we want to link the specific evidence items
        # In this system, 'rejected' validation events are our source of truth for contradictions
        self._link_rejected_evidence(profile_id, candidate_id)

        # Update profile with aggregated contradiction metrics
        total_evidence = profile.get("evidence_count", 1) or 1
        contra_count = metrics.get("contradiction_count", 0)
        ratio = contra_count / total_evidence

        summary = f"Contradiction ratio is {ratio:.1%}. "
        if contra_count > 0:
            summary += f"Found {contra_count} specific evidence items that conflict with this claim."
        else:
            summary += "No contradicting evidence has been observed in the current dataset."

        self.profile_repo.update_profile(
            profile_id,
            contradiction_count=contra_count,
            contradiction_ratio=ratio,
            contradiction_summary=summary
        )

        return contra_count

    def _link_rejected_evidence(self, profile_id, candidate_id):
        """Find rejected evidence items and link them to the profile."""
        # This query finds evidence items linked to the candidate that have 'rejected' validation events
        rows = self.contra_repo.connection.execute(
            """
            SELECT DISTINCT egm.evidence_id, ve.reason
            FROM friction_candidate_groups fcg
            JOIN evidence_group_members egm ON egm.group_id = fcg.evidence_group_id
            JOIN validation_events ve ON ve.evidence_id = egm.evidence_id
            WHERE fcg.friction_candidate_id = ? AND ve.action = 'rejected'
            """,
            (candidate_id,),
        ).fetchall()

        for row in rows:
            self.contra_repo.add_contradiction(
                profile_id=profile_id,
                evidence_id=row["evidence_id"],
                reasoning=row["reason"]
            )

    def get_contradiction_view(self, profile_id):
        """Return full contradiction intelligence for a profile."""
        return self.contra_repo.list_for_profile(profile_id)
