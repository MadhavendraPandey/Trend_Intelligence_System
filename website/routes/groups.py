"""Evidence group routes.

Purpose:
    Render evidence group lists and group detail traceability without changing
    grouping state.

Architecture notes:
    Group pages show Evidence Group -> Evidence -> Post and candidate links
    through repository reads only.

Future extension guidance:
    Keep future grouping actions in explicit workflow routes, not in these
    read-only inspection pages.
"""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, HTTPException, Request
from website.services.rendering import render
from website.services.repository_provider import repository_scope
from website.services import workbench_queries


def register_routes(app):
    """Register group routes."""

    @app.get("/groups", response_class=HTMLResponse)
    def group_explorer(request: Request):
        with repository_scope(request) as repos:
            group_rows = workbench_queries.groups_page(repos)

        return render(
            request,
            "pages/groups.html",
            {"group_rows": group_rows},
            active="groups",
            title="Evidence Groups",
        )

    @app.get("/groups/{group_id}", response_class=HTMLResponse)
    def group_detail(request: Request, group_id: int):
        with repository_scope(request) as repos:
            detail = workbench_queries.group_detail(repos, group_id)

        if detail is None:
            raise HTTPException(status_code=404, detail="Group not found")

        return render(
            request,
            "pages/group_detail.html",
            detail,
            active="groups",
            title=f"Group {group_id}",
        )

