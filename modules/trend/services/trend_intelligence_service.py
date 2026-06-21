"""Trend Intelligence Bridge Service.

Purpose:
    Bridges the existing trend detection engine with the durable repository.
    Handles trend promotion, snapshotting, and relationship sync.
"""

from modules.trend.engines import trend_engine

class TrendIntelligenceService:
    """Orchestrates trend data lifecycle."""

    def __init__(self, profile_repo, metadata_repo, evidence_repo):
        self.profile_repo = profile_repo
        self.metadata_repo = metadata_repo
        self.evidence_repo = evidence_repo

    def process_trends_from_items(self, items):
        """Analyze items, update profiles, and record snapshots."""
        trends = trend_engine.analyze_trends(items)
        processed = []

        for trend in trends:
            # Promote to Profile
            profile = self.profile_repo.create_or_update_trend(
                title=trend["topic"],
                summary=f"Discovered in {trend['source_count']} sources with {trend['mentions']} mentions.",
                domain=trend["domain"],
                theme=trend["theme"],
                trend_score=trend["trend_score"],
                trend_level=trend["trend_level"],
                confidence=trend["confidence"],
                mentions=trend["mentions"],
                source_count=trend["source_count"],
                category_count=trend["category_count"],
                metadata_json={"top_entities": trend["top_entities"]}
            )

            # Record Snapshot
            self.metadata_repo.create_snapshot(profile["id"], **profile)

            # (Optional) Link evidence - in a full implementation we'd scan posts
            # for the normalized topics discovered here.

            processed.append(profile)

        # Post-process relationships
        self._sync_all_relationships(processed)

        return processed

    def _sync_all_relationships(self, profiles):
        """Discover and link conceptually related trend profiles."""
        # Simple heuristic: Trends in the same theme/domain are related
        for i, p1 in enumerate(profiles):
            for p2 in profiles[i+1:]:
                if p1["theme"] == p2["theme"]:
                    self.metadata_repo.create_relationship(
                        from_id=p1["id"],
                        to_id=p2["id"],
                        rel_type="related",
                        explanation=f"Both trends belong to the '{p1['theme']}' theme."
                    )
                elif p1["domain"] == p2["domain"]:
                    self.metadata_repo.create_relationship(
                        from_id=p1["id"],
                        to_id=p2["id"],
                        rel_type="related",
                        explanation=f"Shared domain: {p1['domain']}."
                    )
