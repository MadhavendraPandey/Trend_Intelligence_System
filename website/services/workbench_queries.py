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
    return {
        "total_posts": repos["posts"].count_posts(),
        "total_evidence": repos["evidence"].count_evidence(),
        "total_groups": repos["groups"].count_groups(),
        "total_candidates": repos["candidates"].count_candidates(),
        "latest_run": latest_run_label(repos["runs"]),
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


def evidence_page(repos, page_num=1, query=None):
    """Return evidence explorer data with optional observation search."""
    evidence_rows = repos["evidence"].list_evidence(limit=1000, offset=0)
    if query:
        term = query.casefold()
        evidence_rows = [
            row
            for row in evidence_rows
            if term in (row.get("observation") or "").casefold()
        ]

    data = paginate(evidence_rows, page_num)
    data["query"] = query or ""
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
        }
        for candidate in candidates
    ]


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
