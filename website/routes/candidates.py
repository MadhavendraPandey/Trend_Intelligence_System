"""Candidate friction inspection routes.

Purpose:
    Render generated candidate frictions and their supporting traceability
    chain without validation, ranking, scoring, or recommendations.

Architecture notes:
    Candidate pages show Candidate -> Group -> Evidence -> Post links using
    repositories only.

Future extension guidance:
    Validated frictions and review actions should be added as separate future
    workflows with explicit mutation boundaries.
"""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, HTTPException, Request
from website.services.rendering import render
from website.services.repository_provider import repository_scope
from website.services import workbench_queries


def register_routes(app):
    """Register candidate routes."""

    @app.get("/candidates", response_class=HTMLResponse)
    def candidate_explorer(request: Request):
        with repository_scope(request) as repos:
            candidate_rows = workbench_queries.candidates_page(repos)

        return render(
            request,
            "pages/candidates.html",
            {"candidate_rows": candidate_rows},
            active="candidates",
            title="Candidates",
        )

    @app.get("/candidates/{candidate_id}", response_class=HTMLResponse)
    def candidate_detail(request: Request, candidate_id: int):
        with repository_scope(request) as repos:
            detail = workbench_queries.candidate_detail(repos, candidate_id)

        if detail is None:
            raise HTTPException(status_code=404, detail="Candidate not found")

        return render(
            request,
            "pages/candidate_detail.html",
            detail,
            active="candidates",
            title=f"Candidate {candidate_id}",
        )

