"""Top-level Trend Workbench queries.

Purpose:
    Shape trend intelligence data for the frontend templates.
"""

def trend_dashboard_summary(repos):
    all_trends = repos["trend_profiles"].list_trends(limit=50)

    emerging = [t for t in all_trends if t["trend_level"] == "EMERGING"][:5]
    growing = [t for t in all_trends if t["trend_level"] == "STRONG"][:5]
    dominant = [t for t in all_trends if t["trend_level"] == "DOMINANT"][:5]

    # Domain specific signals
    ai_signals = [t for t in all_trends if t["domain"] == "Artificial Intelligence"][:5]
    sec_signals = [t for t in all_trends if t["domain"] == "Cybersecurity"][:5]

    return {
        "total_trends": repos["trend_profiles"].count_trends(),
        "emerging": emerging,
        "growing": growing,
        "dominant": dominant,
        "ai_signals": ai_signals,
        "sec_signals": sec_signals,
    }

def trend_detail(repos, trend_id):
    trend = repos["trend_profiles"].get_trend(trend_id)
    if not trend:
        return None

    snapshots = repos["trend_metadata"].list_snapshots(trend_id)
    relationships = repos["trend_metadata"].list_relationships(trend_id)
    evidence = repos["trend_profiles"].list_evidence_for_trend(trend_id)

    # Format relationships
    formatted_rels = []
    for r in relationships:
        other_id = r["to_trend_id"] if r["from_trend_id"] == trend_id else r["from_trend_id"]
        other = repos["trend_profiles"].get_trend(other_id)
        formatted_rels.append({
            "rel": r,
            "other": other
        })

    return {
        "trend": trend,
        "snapshots": snapshots,
        "relationships": formatted_rels,
        "evidence": evidence
    }

def trend_graph_data(repos):
    trends = repos["trend_profiles"].list_trends(limit=100)
    nodes = []
    links = []

    seen_ids = set()
    for t in trends:
        nodes.append({"id": t["id"], "label": t["title"], "score": t["trend_score"]})
        seen_ids.add(t["id"])

    # We could fetch all relationships, but for a global graph we'll be selective
    for t in trends:
        rels = repos["trend_metadata"].list_relationships(t["id"])
        for r in rels:
            if r["from_trend_id"] in seen_ids and r["to_trend_id"] in seen_ids:
                links.append({
                    "source": r["from_trend_id"],
                    "target": r["to_trend_id"],
                    "type": r["relationship_type"]
                })

    return {"nodes": nodes, "links": links}

def trend_sources_page(repos):
    sources = repos["sources"].list_sources(limit=100)

    # Enrich with trend contribution counts
    enriched = []
    for s in sources:
        # In a real app we'd have a many-to-many link or source_id on trend_profiles
        # Here we'll simulate observation count per source
        obs_count = repos["evidence"].connection.execute(
            "SELECT COUNT(*) FROM evidence WHERE source_type = ?", (s["source_type"],)
        ).fetchone()[0]

        enriched.append({
            "source": s,
            "observation_count": obs_count
        })

    return enriched
