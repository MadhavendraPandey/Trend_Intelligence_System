"""Source run inspection routes.

Purpose:
    Provide read-only visibility into collection/source run activity.

Architecture notes:
    Runs are operational lineage, not intelligence output. This route uses
    SourceRunRepository and SourceRepository read methods only.

Future extension guidance:
    Add source health pages when operational needs justify them. Keep health
    derived from source runs until a dedicated table is approved.
"""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, Request
from website.services.rendering import render
from website.services.repository_provider import repository_scope
from website.services import workbench_queries


def register_routes(app):
    """Register run routes."""

    @app.get("/runs", response_class=HTMLResponse)
    def runs_page(request: Request):
        with repository_scope(request) as repos:
            run_data = workbench_queries.runs_page(repos)

        return render(
            request,
            "pages/runs.html",
            run_data,
            active="runs",
            title="Runs",
        )
