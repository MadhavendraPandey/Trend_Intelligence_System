"""Evidence explorer routes.

Purpose:
    Let humans inspect evidence records, source posts, and downstream
    traceability links without mutating intelligence data.

Architecture notes:
    Routes use repository-backed services only. No extraction, grouping,
    validation, or scoring behavior belongs here.

Future extension guidance:
    Add repository-backed search and filters when evidence volume grows.
"""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, HTTPException, Request
from website.services.rendering import render
from website.services.repository_provider import repository_scope
from website.services import workbench_queries


def register_routes(app):
    """Register evidence routes."""

    @app.get("/evidence", response_class=HTMLResponse)
    def list_evidence(request: Request, page: int = 1, q: str = None, type: str = None):
        with repository_scope(request) as repos:
            data = workbench_queries.evidence_page(repos, page_num=page, query=q, source_type=type)

        return render(
            request,
            "pages/evidence.html",
            data,
            active="evidence",
            title="Evidence",
        )

    @app.get("/evidence/{evidence_id}", response_class=HTMLResponse)
    def evidence_detail(request: Request, evidence_id: int):
        with repository_scope(request) as repos:
            detail = workbench_queries.evidence_detail(repos, evidence_id)

        if detail["evidence"] is None:
            raise HTTPException(status_code=404, detail="Evidence not found")

        return render(
            request,
            "pages/evidence_detail.html",
            detail,
            active="evidence",
            title=f"Evidence {evidence_id}",
        )

