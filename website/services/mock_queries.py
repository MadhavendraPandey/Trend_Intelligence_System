"""Mock query helpers for the intelligence product flow."""

from __future__ import annotations

def landing_cards():
    return [
        {
            "title": "Trend Intelligence",
            "description": "Discover what is changing. Analyze emerging technologies, tools, research, startups, and signals.",
            "href": "/trend/reports",
            "button": "Explore Trends",
            "tone": "trend",
        },
        {
            "title": "Friction Intelligence",
            "description": "Discover recurring problems and unmet needs. Analyze repeated complaints, blockers, failures, and pain points.",
            "href": "/friction/reports",
            "button": "Explore Frictions",
            "tone": "friction",
        },
    ]

def report_list(domain, q=None, source_type=None, sort="updated_desc", page=1):
    report_type = "Trend" if domain == "trend" else "Friction"
    rows = [
        {
            "report": {"id": 1, "title": f"Mock {report_type} Report 1"},
            "summary": f"This is a mock summary for {report_type} report 1.",
            "evidence_count": 5,
            "source_count": 2,
            "last_updated": "2023-10-27",
            "report_type": report_type,
        },
        {
            "report": {"id": 2, "title": f"Mock {report_type} Report 2"},
            "summary": f"This is a mock summary for {report_type} report 2.",
            "evidence_count": 3,
            "source_count": 1,
            "last_updated": "2023-10-26",
            "report_type": report_type,
        }
    ]
    return {
        "rows": rows,
        "page": 1,
        "total": len(rows),
        "previous_page": None,
        "next_page": None,
        "query": q or "",
        "source_type": source_type or "",
        "sort": sort,
        "report_type": domain,
        "cards": landing_cards(),
    }

def report_detail(domain, report_id):
    report_type = "Trend" if domain == "trend" else "Friction"
    return {
        "report": {"id": report_id, "title": f"Mock {report_type} Report {report_id}"},
        "report_type": report_type,
        "executive_summary": f"Executive summary for mock {report_type} report {report_id}.",
        "description": "Detailed description of the mock report.",
        "evidence_count": 2,
        "source_count": 1,
        "created_at": "2023-10-25",
        "updated_at": "2023-10-27",
        "evidence_items": [
            {
                "evidence": {
                    "observation": "Mock observation 1",
                    "evidence_type": "complaint",
                    "published_at": "2023-10-26",
                    "source_url": "https://example.com/1"
                },
                "source": {"name": "Mock Source A", "source_type": "rss"}
            },
            {
                "evidence": {
                    "observation": "Mock observation 2",
                    "evidence_type": "signal",
                    "published_at": "2023-10-27",
                    "source_url": "https://example.com/2"
                },
                "source": {"name": "Mock Source B", "source_type": "github"}
            }
        ],
        "sources": [
            {
                "source": {"id": 1, "name": "Mock Source A", "source_type": "rss"},
                "observation_count": 1,
                "last_seen": "2023-10-26"
            }
        ],
    }

def evidence_detail(evidence_id):
    return {
        "evidence": {
            "evidence_id": evidence_id,
            "observation": f"Mock observation for evidence {evidence_id}",
            "evidence_type": "complaint",
            "published_at": "2023-10-26",
            "source_url": "https://example.com/e1",
            "content": "Full content of the mock evidence."
        },
        "post": {"id": 1, "url": "https://example.com/p1", "title": "Mock Post"},
        "source": {"id": 1, "name": "Mock Source A", "source_type": "rss"},
        "group_links": []
    }

def source_detail(source_id):
    return {
        "source": {
            "id": source_id,
            "name": f"Mock Source {source_id}",
            "source_type": "rss",
            "base_url": "https://example.com/rss",
            "description": "Mock source description"
        },
        "post_count": 10,
        "run_count": 5,
        "latest_run": {"id": 1, "completed_at": "2023-10-27"},
        "posts": [],
        "runs": []
    }

def operator_summary():
    return {
        "summary": {
            "db_size_mb": 1.5,
            "total_tables": 12,
            "table_counts": {
                "posts": 100,
                "evidence": 50,
                "sources": 5,
                "friction_profiles": 10
            },
            "latest_run": {
                "id": 1,
                "started_at": "2023-10-27 10:00:00",
                "status": "completed",
                "items_stored": 25
            }
        },
        "orphans": []
    }
