"""Read-only query helpers for the intelligence product flow."""

from __future__ import annotations

from collections import defaultdict


PAGE_SIZE = 20


def _paginate(rows, page_num, page_size=PAGE_SIZE):
    current_page = max(int(page_num or 1), 1)
    total = len(rows)
    start = (current_page - 1) * page_size
    end = start + page_size
    return {
        "rows": rows[start:end],
        "page": current_page,
        "total": total,
        "previous_page": current_page - 1 if current_page > 1 else None,
        "next_page": current_page + 1 if end < total else None,
    }


def _normalize_query(text):
    return (text or "").strip().casefold()


def _report_type_label(domain):
    return "Trend" if domain == "trend" else "Friction"


def _evidence_item(evidence, post=None, source=None):
    return {
        "evidence": evidence,
        "post": post,
        "source": source,
    }


def _source_summary(source, observation_count=0, last_seen=None):
    return {
        "source": source,
        "observation_count": observation_count,
        "last_seen": last_seen,
    }


def landing_cards():
    return [
        {
            "title": "Trend Intelligence",
            "description": "Discover what is changing. Analyze emerging technologies, tools, research, startups, and signals.",
            "href": "/trends",
            "button": "Explore Trends",
            "tone": "trend",
        },
        {
            "title": "Friction Intelligence",
            "description": "Discover recurring problems and unmet needs. Analyze repeated complaints, blockers, failures, and pain points.",
            "href": "/frictions",
            "button": "Explore Frictions",
            "tone": "friction",
        },
    ]


def evidence_page(repos, page_num=1, query=None, source_type=None):
    evidence_rows = repos["evidence"].list_evidence(limit=1000, offset=0)

    if query:
        term = _normalize_query(query)
        evidence_rows = [
            row
            for row in evidence_rows
            if term in (row.get("observation") or "").casefold()
        ]

    if source_type:
        evidence_rows = [row for row in evidence_rows if row.get("source_type") == source_type]

    rows = []
    for evidence in evidence_rows:
        post = repos["posts"].get_post(evidence["post_id"]) if evidence else None
        source = repos["sources"].get_source(post["source_id"]) if post else None
        rows.append(
            {
                "evidence": evidence,
                "post": post,
                "source": source,
            }
        )

    page_data = _paginate(rows, page_num)
    page_data.update({"query": query or "", "source_type": source_type or ""})
    return page_data


def evidence_detail(repos, evidence_id):
    evidence = repos["evidence"].get_evidence(evidence_id)
    post = repos["posts"].get_post(evidence["post_id"]) if evidence else None
    source = repos["sources"].get_source(post["source_id"]) if post else None
    groups = repos["groups"].list_groups_for_evidence(evidence_id) if evidence else []

    candidate_links = []
    for group in groups:
        candidates = repos["candidates"].list_candidates_for_group(group["id"])
        candidate_links.append({"group": group, "candidates": candidates})

    return {
        "evidence": evidence,
        "post": post,
        "source": source,
        "group_links": candidate_links,
    }


def report_list(repos, domain, q=None, source_type=None, sort="updated_desc", page=1):
    if domain == "trend":
        reports = repos["trend_profiles"].list_trends(limit=1000)
        evidence_repo = repos["evidence"]
        source_repo = repos["sources"]
        evidence_loader = lambda report_id: repos["trend_profiles"].list_evidence_for_trend(report_id)
        source_aggregator = _trend_sources_for_report
    else:
        reports = repos["profiles"].list_profiles(status="active", limit=1000)
        evidence_repo = repos["evidence"]
        source_repo = repos["sources"]
        evidence_loader = lambda report_id: _friction_evidence_for_profile(repos, report_id)
        source_aggregator = _friction_sources_for_report

    query = _normalize_query(q)
    if query:
        reports = [
            report
            for report in reports
            if query in (report.get("title") or "").casefold()
            or query in (report.get("summary") or "").casefold()
            or query in (report.get("description") or "").casefold()
        ]

    if source_type:
        filtered = []
        for report in reports:
            report_sources = source_aggregator(repos, report["id"])
            if any(item["source"] and item["source"].get("source_type") == source_type for item in report_sources):
                filtered.append(report)
        reports = filtered

    def sort_key(report):
        if sort == "title_asc":
            return (report.get("title") or "").casefold()
        if sort == "title_desc":
            return (report.get("title") or "").casefold()
        if sort == "evidence_desc":
            return report.get("evidence_count", 0)
        return report.get("updated_at") or report.get("created_at") or ""

    reverse = sort != "title_asc"
    reports = sorted(reports, key=sort_key, reverse=reverse)

    rows = []
    for report in reports:
        evidence_items = evidence_loader(report["id"])
        source_items = source_aggregator(repos, report["id"])
        rows.append(
            {
                "report": report,
                "summary": report.get("summary") or report.get("validation_summary") or "",
                "evidence_count": len(evidence_items),
                "source_count": len(source_items),
                "last_updated": report.get("updated_at") or report.get("created_at"),
                "report_type": _report_type_label(domain),
            }
        )

    page_data = _paginate(rows, page)
    page_data.update(
        {
            "query": q or "",
            "source_type": source_type or "",
            "sort": sort,
            "report_type": domain,
            "cards": landing_cards(),
        }
    )
    return page_data


def sources_page(repos):
    source_rows = []
    for source in repos["sources"].list_sources(limit=1000):
        source_rows.append(
            {
                "source": source,
                "post_count": repos["posts"].count_posts(source_id=source["id"]),
                "run_count": repos["runs"].count_runs(source_id=source["id"]),
                "latest_run": repos["runs"].latest_run(source_id=source["id"]),
            }
        )
    return source_rows


def source_detail(repos, source_id):
    source = repos["sources"].get_source(source_id)
    if source is None:
        return None

    return {
        "source": source,
        "post_count": repos["posts"].count_posts(source_id=source_id),
        "run_count": repos["runs"].count_runs(source_id=source_id),
        "latest_run": repos["runs"].latest_run(source_id=source_id),
        "posts": repos["posts"].list_posts(source_id=source_id, limit=50),
        "runs": repos["runs"].list_runs(source_id=source_id, limit=20),
    }


def report_detail(repos, domain, report_id):
    if domain == "trend":
        report = repos["trend_profiles"].get_trend(report_id)
        if not report:
            return None
        evidence_items = [
            _build_evidence_bundle(repos, evidence)
            for evidence in repos["trend_profiles"].list_evidence_for_trend(report_id)
        ]
        sources = _aggregate_sources_from_evidence(evidence_items)
    else:
        report = repos["profiles"].get_profile(report_id)
        if not report:
            return None
        evidence_items = _friction_detail_evidence(repos, report_id)
        sources = _aggregate_sources_from_evidence(evidence_items)

    return {
        "report": report,
        "report_type": _report_type_label(domain),
        "executive_summary": report.get("summary") or report.get("validation_summary") or report.get("description") or "",
        "description": report.get("description") or "",
        "evidence_count": len(evidence_items),
        "source_count": len(sources),
        "created_at": report.get("created_at"),
        "updated_at": report.get("updated_at"),
        "evidence_items": evidence_items,
        "sources": sources,
    }


def global_search(repos, q="", domain=""):
    query = _normalize_query(q)
    domain = (domain or "").strip().casefold()

    result = {
        "query": q or "",
        "domain": domain,
        "trend_reports": [],
        "friction_reports": [],
        "evidence": [],
        "sources": [],
    }

    if query:
        trend_reports = report_list(repos, "trend", q=query)["rows"]
        friction_reports = report_list(repos, "friction", q=query)["rows"]
        result["trend_reports"] = trend_reports if domain in ("", "trend") else []
        result["friction_reports"] = friction_reports if domain in ("", "friction") else []
        result["evidence"] = _search_evidence(repos, query)
        result["sources"] = _search_sources(repos, query)

    return result


def _trend_sources_for_report(repos, trend_id):
    items = []
    seen = set()
    for evidence in repos["trend_profiles"].list_evidence_for_trend(trend_id):
        bundle = _build_evidence_bundle(repos, evidence)
        source = bundle["source"]
        if source and source["id"] not in seen:
            seen.add(source["id"])
            items.append(source)
    return items


def _friction_evidence_for_profile(repos, profile_id):
    evidence_items = []
    seen = set()
    candidate = repos["profiles"].get_profile(profile_id)
    if not candidate or not candidate.get("candidate_friction_id"):
        return evidence_items

    for link in repos["candidates"].list_groups(candidate["candidate_friction_id"], limit=1000):
        group = repos["groups"].get_group(link["evidence_group_id"])
        if not group:
            continue
        for member in repos["groups"].list_members(group["id"], limit=1000):
            evidence = repos["evidence"].get_evidence(member["evidence_id"])
            if evidence and evidence["evidence_id"] not in seen:
                seen.add(evidence["evidence_id"])
                evidence_items.append(_build_evidence_bundle(repos, evidence))

    return evidence_items


def _friction_sources_for_report(repos, profile_id):
    return _aggregate_sources_from_evidence(_friction_detail_evidence(repos, profile_id))


def _friction_detail_evidence(repos, profile_id):
    return _friction_evidence_for_profile(repos, profile_id)


def _build_evidence_bundle(repos, evidence):
    post = repos["posts"].get_post(evidence["post_id"]) if evidence else None
    source = repos["sources"].get_source(post["source_id"]) if post else None
    return _evidence_item(evidence, post, source)


def _aggregate_sources_from_evidence(evidence_items):
    grouped = {}
    for item in evidence_items:
        source = item.get("source")
        if not source:
            continue
        source_id = source["id"]
        grouped.setdefault(
            source_id,
            {
                "source": source,
                "observation_count": 0,
                "last_seen": None,
            },
        )
        grouped[source_id]["observation_count"] += 1
        seen = item["evidence"].get("captured_at") or item["evidence"].get("published_at")
        if seen and (grouped[source_id]["last_seen"] is None or seen > grouped[source_id]["last_seen"]):
            grouped[source_id]["last_seen"] = seen
    return list(grouped.values())


def _search_evidence(repos, query):
    matches = []
    for evidence in repos["evidence"].list_evidence(limit=1000):
        if query in (evidence.get("observation") or "").casefold():
            matches.append(_build_evidence_bundle(repos, evidence))
    return matches


def _search_sources(repos, query):
    matches = []
    for source in repos["sources"].list_sources(limit=1000):
        text = " ".join(
            str(value or "").casefold()
            for value in (source.get("name"), source.get("source_type"), source.get("base_url"))
        )
        if query in text:
            matches.append(
                _source_summary(
                    source,
                    observation_count=_source_observation_count(repos, source["id"]),
                    last_seen=_source_last_seen(repos, source["id"]),
                )
            )
    return matches


def _source_observation_count(repos, source_id):
    return repos["evidence"].connection.execute(
        "SELECT COUNT(*) FROM evidence e JOIN posts p ON p.id = e.post_id WHERE p.source_id = ?",
        (source_id,),
    ).fetchone()[0]


def _source_last_seen(repos, source_id):
    row = repos["evidence"].connection.execute(
        """
        SELECT MAX(COALESCE(e.captured_at, e.published_at))
        FROM evidence e
        JOIN posts p ON p.id = e.post_id
        WHERE p.source_id = ?
        """,
        (source_id,),
    ).fetchone()
    return row[0] if row else None
