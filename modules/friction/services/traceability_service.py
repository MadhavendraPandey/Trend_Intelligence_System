"""Traceability service for friction intelligence.

Purpose:
    Build the complete chain of evidence from Friction Profiles back to
    original sources. This service enables transparent explainability.

Architecture notes:
    The service traverses relationships:
    Profile -> Candidate -> Group -> Evidence -> Post -> Source
"""

from database.repositories.friction_candidate_repository import FrictionCandidateRepository
from database.repositories.evidence_group_repository import EvidenceGroupRepository
from database.repositories.evidence_repository import EvidenceRepository
from database.repositories.post_repository import PostRepository
from database.repositories.source_repository import SourceRepository


class TraceabilityService:
    """Service for building evidence and source chains."""

    def __init__(self, repos):
        self.candidate_repo = repos["candidates"]
        self.group_repo = repos["groups"]
        self.evidence_repo = repos["evidence"]
        self.post_repo = repos["posts"]
        self.source_repo = repos["sources"]

    def build_profile_chain(self, candidate_id):
        """Build the complete traceability tree for a validated candidate."""
        # 1. Groups for Candidate
        group_links = self.candidate_repo.list_groups(candidate_id, limit=1000)

        trace_groups = []
        for link in group_links:
            group_id = link["evidence_group_id"]
            group = self.group_repo.get_group(group_id)
            if not group:
                continue

            # 2. Evidence for Group
            evidence_members = []
            member_links = self.group_repo.list_members(group_id, limit=1000)

            for m_link in member_links:
                evidence_id = m_link["evidence_id"]
                evidence = self.evidence_repo.get_evidence(evidence_id)
                if not evidence:
                    continue

                # 3. Post for Evidence
                post = self.post_repo.get_post(evidence["post_id"])

                # 4. Source for Post
                source = None
                if post:
                    source = self.source_repo.get_source(post["source_id"])

                evidence_members.append({
                    "evidence": evidence,
                    "post": post,
                    "source": source
                })

            trace_groups.append({
                "group": group,
                "evidence_members": evidence_members
            })

        return trace_groups

    def build_evidence_origin(self, evidence_id):
        """Build the source-wards chain for an individual evidence record."""
        evidence = self.evidence_repo.get_evidence(evidence_id)
        if not evidence:
            return None

        post = self.post_repo.get_post(evidence["post_id"])
        source = self.source_repo.get_source(post["source_id"]) if post else None

        # Related groups and frictions
        groups = self.group_repo.list_groups_for_evidence(evidence_id)
        frictions = []
        for group in groups:
            candidates = self.candidate_repo.list_candidates_for_group(group["id"])
            frictions.extend(candidates)

        return {
            "evidence": evidence,
            "post": post,
            "source": source,
            "related_groups": groups,
            "related_frictions": frictions
        }
