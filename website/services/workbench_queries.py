"""Read-only view queries for workbench pages.

Purpose:
    Shape repository results into stable template data for dashboard,
    explorers, and traceability views.

Architecture notes:
    This module calls repositories only. It does not execute SQL and does not
    mutate intelligence data.

Future extension guidance:
    Replace in-memory filtering with repository search methods when search
    becomes large enough to justify database-backed querying.
"""

from __future__ import annotations


PAGE_SIZE = 20


def latest_run_label(run_repository):
    """Return a compact latest-run label for dashboard metrics."""
    latest = run_repository.latest_run()
    if latest is None:
        return "No runs yet"

    when = latest.get("finished_at") or latest.get("started_at") or "Unknown time"
    return f"{when} ({latest.get('status')})"


def dashboard_summary(repos):
    """Return top-level workbench metrics."""
    # Derived dashboard sections
    all_profiles = repos["profiles"].list_profiles(status="active", limit=100)

    fastest_growing = sorted(
        [p for p in all_profiles if p.get("latest_classification") == "GROWING"],
        key=lambda x: x.get("evidence_count", 0),
        reverse=True
    )[:5]

    most_contradicted = sorted(
        all_profiles,
        key=lambda x: x.get("contradiction_ratio", 0.0),
        reverse=True
    )[:5]

    most_connected = []
    for p in all_profiles:
        p["rel_count"] = len(repos["relationships"].list_for_profile(p["id"]))
        most_connected.append(p)
    most_connected = sorted(most_connected, key=lambda x: x["rel_count"], reverse=True)[:5]

    return {
        "total_posts": repos["posts"].count_posts(),
        "total_evidence": repos["evidence"].count_evidence(),
        "total_groups": repos["groups"].count_groups(),
        "total_candidates": repos["candidates"].count_candidates(),
        "total_profiles": repos["profiles"].count_profiles(),
        "latest_run": latest_run_label(repos["runs"]),
        "fastest_growing": fastest_growing,
        "most_contradicted": most_contradicted,
        "most_connected": most_connected
    }


def paginate(rows, page_num, page_size=PAGE_SIZE):
    """Return a simple pagination view-model for already-filtered rows."""
    current_page = max(int(page_num or 1), 1)
    total = len(rows)
    start = (current_page - 1) * page_size
    end = start + page_size
    return {
        "rows": rows[start:end],
        "page": current_page,
        "total": total,
        "page_size": page_size,
        "previous_page": current_page - 1 if current_page > 1 else None,
        "next_page": current_page + 1 if end < total else None,
    }


def evidence_page(repos, page_num=1, query=None, source_type=None):
    """Return evidence explorer data with search and type filtering."""
    evidence_rows = repos["evidence"].list_evidence(limit=1000, offset=0)

    if query:
        term = query.casefold()
        evidence_rows = [
            row
            for row in evidence_rows
            if term in (row.get("observation") or "").casefold()
        ]

    if source_type:
        evidence_rows = [row for row in evidence_rows if row.get("source_type") == source_type]

    data = paginate(evidence_rows, page_num)
    data["query"] = query or ""
    data["source_type"] = source_type or ""
    return data


def evidence_detail(repos, evidence_id):
    """Return one evidence record and its source post."""
    evidence = repos["evidence"].get_evidence(evidence_id)
    post = repos["posts"].get_post(evidence["post_id"]) if evidence else None
    groups = repos["groups"].list_groups_for_evidence(evidence_id) if evidence else []

    candidate_links = []
    for group in groups:
        candidates = repos["candidates"].list_candidates_for_group(group["id"])
        candidate_links.append({"group": group, "candidates": candidates})

    return {
        "evidence": evidence,
        "post": post,
        "group_links": candidate_links,
    }


def groups_page(repos):
    """Return evidence groups with member counts."""
    groups = repos["groups"].list_groups(limit=1000)
    return [
        {
            "group": group,
            "member_count": repos["groups"].count_members(group["id"]),
            "candidate_count": len(
                repos["candidates"].list_candidates_for_group(group["id"])
            ),
        }
        for group in groups
    ]


def group_detail(repos, group_id):
    """Return a group, member evidence, source posts, and candidate links."""
    group = repos["groups"].get_group(group_id)
    if group is None:
        return None

    members = []
    for member in repos["groups"].list_members(group_id, limit=1000):
        evidence = repos["evidence"].get_evidence(member["evidence_id"])
        post = repos["posts"].get_post(evidence["post_id"]) if evidence else None
        members.append({"membership": member, "evidence": evidence, "post": post})

    return {
        "group": group,
        "members": members,
        "candidates": repos["candidates"].list_candidates_for_group(group_id),
    }


def candidates_page(repos):
    """Return friction candidates with supporting group counts."""
    candidates = repos["candidates"].list_candidates(limit=1000)
    return [
        {
            "candidate": candidate,
            "group_count": repos["candidates"].count_group_links(candidate["id"]),
            "profile": repos["profiles"].get_profile_by_candidate(candidate["id"]),
        }
        for candidate in candidates
    ]


def profiles_page(repos, query=None, classification=None):
    """Return active friction profiles with search and classification filter."""
    profiles = repos["profiles"].list_profiles(status="active", limit=1000)

    if query:
        term = query.casefold()
        profiles = [p for p in profiles if term in p["title"].casefold() or term in (p.get("description") or "").casefold()]

    if classification:
        profiles = [p for p in profiles if p.get("latest_classification") == classification]

    return [
        {
            "profile": profile,
            "snapshot_count": len(repos["snapshots"].list_for_profile(profile["id"])),
            "relationship_count": len(repos["relationships"].list_for_profile(profile["id"])),
        }
        for profile in profiles
    ]


def graph_page(repos):
    """Return data for the global reality graph view."""
    profiles = profiles_page(repos)
    relationships = repos["relationships"].list_all()

    formatted_rels = []
    for rel in relationships:
        from_p = repos["profiles"].get_profile(rel["from_profile_id"])
        to_p = repos["profiles"].get_profile(rel["to_profile_id"])
        if from_p and to_p:
            formatted_rels.append({
                **rel,
                "from_title": from_p["title"],
                "to_title": to_p["title"]
            })

    return {
        "profiles": profiles,
        "all_relationships": formatted_rels
    }


def profile_detail(repos, profile_id):
    """Return profile data and full traceability chain."""
    profile = repos["profiles"].get_profile(profile_id)
    if not profile:
        return None

    # Use traceability service logic (inlined for query module)
    trace_groups = []
    if profile.get("candidate_friction_id"):
        candidate_id = profile["candidate_friction_id"]
        group_links = repos["candidates"].list_groups(candidate_id, limit=1000)

        for link in group_links:
            group = repos["groups"].get_group(link["evidence_group_id"])
            if not group:
                continue

            evidence_members = []
            for m_link in repos["groups"].list_members(group["id"], limit=1000):
                evidence = repos["evidence"].get_evidence(m_link["evidence_id"])
                post = (
                    repos["posts"].get_post(evidence["post_id"]) if evidence else None
                )
                source = (
                    repos["sources"].get_source(post["source_id"]) if post else None
                )
                evidence_members.append(
                    {
                        "evidence": evidence,
                        "post": post,
                        "source": source,
                    }
                )

            trace_groups.append(
                {
                    "group": group,
                    "evidence_members": evidence_members,
                }
            )

    # Maturity Layer data
    snapshots = repos["snapshots"].list_for_profile(profile_id)
    relationships = repos["relationships"].list_for_profile(profile_id)
    contradictions = repos["contradictions"].list_for_profile(profile_id)

    # Format relationships for graph or list
    formatted_rels = []
    for r in relationships:
        other_id = r["to_profile_id"] if r["from_profile_id"] == profile_id else r["from_profile_id"]
        other = repos["profiles"].get_profile(other_id)
        formatted_rels.append({
            "rel": r,
            "other": other,
            "is_source": r["from_profile_id"] == profile_id
        })

    return {
        "profile": profile,
        "trace_groups": trace_groups,
        "snapshots": snapshots,
        "relationships": formatted_rels,
        "contradictions": contradictions
    }


def candidate_detail(repos, candidate_id):
    """Return a candidate with complete group, evidence, and post traceability."""
    candidate = repos["candidates"].get_candidate(candidate_id)
    if candidate is None:
        return None

    trace_groups = []
    for link in repos["candidates"].list_groups(candidate_id, limit=1000):
        group = repos["groups"].get_group(link["evidence_group_id"])
        if group is None:
            continue

        evidence_members = []
        for member in repos["groups"].list_members(group["id"], limit=1000):
            evidence = repos["evidence"].get_evidence(member["evidence_id"])
            post = repos["posts"].get_post(evidence["post_id"]) if evidence else None
            evidence_members.append(
                {
                    "membership": member,
                    "evidence": evidence,
                    "post": post,
                }
            )

        trace_groups.append(
            {
                "link": link,
                "group": group,
                "evidence_members": evidence_members,
            }
        )

    return {
        "candidate": candidate,
        "trace_groups": trace_groups,
    }


def runs_page(repos):
    """Return operational source run data for inspection."""
    runs = repos["runs"].list_runs(limit=100)
    return {
        "runs": runs,
        "total_runs": repos["runs"].count_runs(),
        "sources": repos["sources"].list_sources(limit=1000),
        "latest_run": repos["runs"].latest_run(),
    }
