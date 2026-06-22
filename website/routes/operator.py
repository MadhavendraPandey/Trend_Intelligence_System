"""Routes for the Internal Operator Console."""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, Request
from website.services.rendering import render
from website.services.repository_provider import repository_scope


def register_routes(app):
    """Register operator routes."""

    @app.get("/operator", response_class=HTMLResponse)
    def operator_dashboard(request: Request):
        with repository_scope(request) as repos:
            summary = repos["operator"].get_summary()
            orphans = repos["operator"].list_orphaned_records()

        return render(
            request,
            "pages/operator/dashboard.html",
            {"summary": summary, "orphans": orphans},
            active="operator",
            title="Operator Console",
        )
