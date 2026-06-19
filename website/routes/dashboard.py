"""Dashboard and future-section placeholder routes.

Purpose:
    Render the workbench home page and intentional placeholders for navigation
    sections that are architecturally planned but not yet implemented.

Architecture notes:
    These routes are read-only and repository-backed. Placeholders prevent
    navigation dead ends without creating intelligence behavior.

Future extension guidance:
    Replace placeholder pages with dedicated route modules as each section
    becomes a real workflow.
"""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, Request
from website.services.rendering import render
from website.services.repository_provider import repository_scope
from website.services.workbench_queries import dashboard_summary


def register_routes(app):
    """Register dashboard routes."""

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request):
        with repository_scope(request) as repos:
            summary = dashboard_summary(repos)

        return render(
            request,
            "pages/dashboard.html",
            {"summary": summary},
            active="dashboard",
            title="Dashboard",
        )

    @app.get("/sources", response_class=HTMLResponse)
    def sources_placeholder(request: Request):
        return _placeholder(request, "Sources", "sources")

    @app.get("/posts", response_class=HTMLResponse)
    def posts_placeholder(request: Request):
        return _placeholder(request, "Posts", "posts")

    @app.get("/validation", response_class=HTMLResponse)
    def validation_placeholder(request: Request):
        return _placeholder(request, "Validation Queue", "validation")

    @app.get("/decisions", response_class=HTMLResponse)
    def decisions_placeholder(request: Request):
        return _placeholder(request, "Decisions", "decisions")

    @app.get("/metrics", response_class=HTMLResponse)
    def metrics_placeholder(request: Request):
        return _placeholder(request, "Metrics", "metrics")

    @app.get("/settings", response_class=HTMLResponse)
    def settings_placeholder(request: Request):
        return _placeholder(request, "Settings", "settings")


def _placeholder(request, section_name, active):
    return render(
        request,
        "pages/placeholder.html",
        {
            "section_name": section_name,
            "message": (
                "This section is reserved in the workbench architecture and "
                "will be implemented in a later phase."
            ),
        },
        active=active,
        title=section_name,
    )
