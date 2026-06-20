"""Friction Profile management service.

Purpose:
    Convert validated candidate frictions into durable Friction Profiles.
    Profiles aggregate metrics and summaries to provide a canonical identity
    for evidence-backed frictions.

Philosophy:
    The system discovers and organizes reality. Descriptions remain factual
    and evidence-based. No recommendations or business advice are included.
"""

from database.repositories.friction_candidate_repository import FrictionCandidateRepository
from database.repositories.friction_profile_repository import FrictionProfileRepository


class FrictionProfileService:
    """Service for creating and updating Friction Profiles."""

    def __init__(self, candidate_repository, profile_repository):
        if not isinstance(candidate_repository, FrictionCandidateRepository):
            raise TypeError("ProfileService requires FrictionCandidateRepository")
        if not isinstance(profile_repository, FrictionProfileRepository):
            raise TypeError("ProfileService requires FrictionProfileRepository")

        self.candidate_repository = candidate_repository
        self.profile_repository = profile_repository

    def sync_accepted_candidates(self):
        """Convert all 'accepted' candidates into persistent profiles."""
        candidates = self.candidate_repository.list_candidates(status="accepted", limit=1000)
        synced = []

        for candidate in candidates:
            profile = self.sync_candidate_to_profile(candidate)
            synced.append(profile)

        return synced

    def sync_candidate_to_profile(self, candidate):
        """Generate or update a Friction Profile from one candidate."""
        existing = self.profile_repository.get_profile_by_candidate(candidate["id"])

        # Prepare profile fields from candidate
        profile_data = {
            "title": candidate["title"],
            "description": candidate["description"],
            "validation_summary": candidate.get("validation_summary"),
            "evidence_count": candidate.get("evidence_count", 0),
            "source_count": candidate.get("source_count", 0),
            "group_count": candidate.get("group_count", 0),
            "post_count": candidate.get("post_count", 0),
            "recurrence_count": candidate.get("recurrence_count", 0),
            "contradiction_count": candidate.get("contradiction_count", 0),
            "status": "active",
        }

        if existing:
            return self.profile_repository.update_profile(existing["id"], **profile_data)

        return self.profile_repository.create_profile(
            candidate_friction_id=candidate["id"],
            **profile_data
        )

    def get_profile_view(self, profile_id):
        """Assemble a complete profile view for the workbench."""
        profile = self.profile_repository.get_profile(profile_id)
        if not profile:
            return None

        candidate = None
        if profile.get("candidate_friction_id"):
            candidate = self.candidate_repository.get_candidate(profile["candidate_friction_id"])

        return {
            "profile": profile,
            "candidate": candidate
        }
