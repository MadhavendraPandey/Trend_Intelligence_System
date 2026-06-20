"""Friction Evolution service for temporal intelligence.

Purpose:
    Track the growth and change of friction profiles over time.
    Provide rule-based, evidence-backed classification of evolution states.

Philosophy:
    No forecasting or predictions. Only classify observed historical changes
    based on evidence metrics. Reasoning must be provided for every
    classification.
"""

from datetime import datetime, timedelta


class EvolutionService:
    """Service for snapshotting profiles and classifying their evolution."""

    CLASSIFICATIONS = {
        "EMERGING": "Recently discovered with low but growing evidence.",
        "GROWING": "Significant increase in evidence and sources over time.",
        "STABLE": "Consistent evidence recurrence without rapid growth.",
        "DECLINING": "Reduced recurrence in recent observation windows.",
        "DORMANT": "No new evidence observed in the last 30 days.",
    }

    def __init__(self, profile_repository, snapshot_repository):
        self.profile_repo = profile_repository
        self.snapshot_repo = snapshot_repository

    def process_profile_evolution(self, profile_id):
        """Record a snapshot and update the profile's evolution state."""
        profile = self.profile_repo.get_profile(profile_id)
        if not profile:
            return None

        # 1. Create immutable snapshot of current state
        self.snapshot_repo.create_snapshot(profile_id, **profile)

        # 2. Analyze history to determine classification
        snapshots = self.snapshot_repo.list_for_profile(profile_id, limit=10)

        classification, reasoning = self.classify_evolution(profile, snapshots)

        # 3. Update profile with latest intelligence
        return self.profile_repo.update_profile(
            profile_id,
            latest_classification=classification,
            latest_classification_reasoning=reasoning
        )

    def classify_evolution(self, current, history):
        """Determine evolution state based on historical comparison."""
        if not history or len(history) < 2:
            return "EMERGING", "First observation or insufficient historical data to determine growth trend."

        # Compare with the oldest snapshot in the window (usually the first one recorded)
        oldest = history[-1]

        evidence_growth = current["evidence_count"] - oldest["evidence_count"]
        source_growth = current["source_count"] - oldest["source_count"]

        # Check for dormancy (assuming snapshot_at is ISO string)
        last_updated = datetime.fromisoformat(current["updated_at"].replace(' ', 'T'))
        if datetime.utcnow() - last_updated > timedelta(days=30):
             return "DORMANT", "No new evidence or updates observed in the last 30 days."

        if evidence_growth > 5 or source_growth > 2:
            return "GROWING", f"Evidence count increased from {oldest['evidence_count']} to {current['evidence_count']} since {oldest['snapshot_at']}."

        if evidence_growth == 0:
            return "STABLE", "Evidence count has remained constant across observation windows."

        if evidence_growth < 0:
             return "DECLINING", "Observed evidence count in active window has decreased compared to historical records."

        return "STABLE", "Consistent evidence presence with minor fluctuations."

    def get_timeline(self, profile_id):
        """Return historical snapshots for timeline visualization."""
        return self.snapshot_repo.list_for_profile(profile_id)
