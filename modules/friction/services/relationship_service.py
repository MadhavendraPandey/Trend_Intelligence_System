"""Relationship discovery service for friction-to-friction mapping.

Purpose:
    Discover and persist connections between different friction profiles.
    Enable the creation of a navigable intelligence graph.

Philosophy:
    Relationships must be evidence-backed. Explanations should focus on
    observable overlaps or dependencies.
"""

class RelationshipService:
    """Service for discovering and managing inter-friction relationships."""

    def __init__(self, relationship_repository, profile_repository):
        self.rel_repo = relationship_repository
        self.profile_repo = profile_repository

    def discover_relationships(self, profile_id):
        """Analyze a profile against others to find overlaps or links."""
        target_profile = self.profile_repo.get_profile(profile_id)
        if not target_profile:
            return []

        all_profiles = self.profile_repo.list_profiles(limit=100)
        discovered = []

        for other in all_profiles:
            if other["id"] == profile_id:
                continue

            # Simple heuristic discovery based on keyword overlap in titles/descriptions
            # In a full implementation, this would use LLM analysis or shared evidence groups
            overlap = self._calculate_content_overlap(target_profile, other)

            if overlap > 0.3:
                rel = self.rel_repo.create_relationship(
                    from_id=profile_id,
                    to_id=other["id"],
                    rel_type="overlapping" if overlap > 0.6 else "related",
                    explanation=f"Significant conceptual overlap detected in descriptions ({int(overlap*100)}%).",
                    supporting_evidence_count=min(target_profile["evidence_count"], other["evidence_count"]),
                    supporting_source_count=min(target_profile["source_count"], other["source_count"])
                )
                discovered.append(rel)

        return discovered

    def _calculate_content_overlap(self, p1, p2):
        """Basic Jaccard similarity between profile titles and descriptions."""
        def get_words(p):
            text = f"{p['title']} {p.get('description', '')}".lower()
            return set(w for w in text.split() if len(w) > 3)

        w1 = get_words(p1)
        w2 = get_words(p2)

        if not w1 or not w2:
            return 0.0

        intersection = w1.intersection(w2)
        union = w1.union(w2)

        return len(intersection) / len(union)

    def get_profile_graph_data(self, profile_id):
        """Return relationship data formatted for graph visualization."""
        rels = self.rel_repo.list_for_profile(profile_id)
        nodes = []
        links = []

        seen_ids = set()

        # Add main node
        main_profile = self.profile_repo.get_profile(profile_id)
        nodes.append({"id": main_profile["id"], "label": main_profile["title"], "type": "main"})
        seen_ids.add(profile_id)

        for r in rels:
            other_id = r["to_profile_id"] if r["from_profile_id"] == profile_id else r["from_profile_id"]

            if other_id not in seen_ids:
                other_profile = self.profile_repo.get_profile(other_id)
                if other_profile:
                    nodes.append({"id": other_id, "label": other_profile["title"], "type": "related"})
                    seen_ids.add(other_id)

            links.append({
                "source": r["from_profile_id"],
                "target": r["to_profile_id"],
                "type": r["relationship_type"],
                "weight": r["supporting_evidence_count"]
            })

        return {"nodes": nodes, "links": links}
