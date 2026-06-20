"""Routes for Friction Profiles exploration.

Purpose:
    Provide routes for listing and inspecting durable Friction Profiles
    and their traceability chains.
"""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, HTTPException, Request
from website.services.rendering import render
from website.services.repository_provider import repository_scope
from website.services import workbench_queries


def register_routes(app):
    """Register profile routes."""

    @app.get("/frictions", response_class=HTMLResponse)
    def list_profiles(request: Request):
        with repository_scope(request) as repos:
            profiles = workbench_queries.profiles_page(repos)

        return render(
            request,
            "pages/profiles.html",
            {"profiles": profiles},
            active="frictions",
            title="Friction Profiles",
        )

    @app.get("/frictions/{profile_id}", response_class=HTMLResponse)
    def view_profile(request: Request, profile_id: int):
        with repository_scope(request) as repos:
            data = workbench_queries.profile_detail(repos, profile_id)

        if not data:
            raise HTTPException(status_code=404, detail="Profile not found")

        return render(
            request,
            "pages/profile_detail.html",
            data,
            active="frictions",
            title=data["profile"]["title"],
        )
