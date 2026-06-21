"""Routes for the Trend Intelligence domain.

Purpose:
    Provide routes for trend dashboard, profiles, and reality graph.
"""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, HTTPException, Request
from website.services.rendering import render
from website.services.repository_provider import repository_scope
from website.services import trend_queries


def register_routes(app):
    """Register trend routes."""

    @app.get("/trends", response_class=HTMLResponse)
    def trend_dashboard(request: Request):
        with repository_scope(request) as repos:
            summary = trend_queries.trend_dashboard_summary(repos)

        return render(
            request,
            "pages/trends/dashboard.html",
            {"summary": summary},
            active="trends",
            title="Trend Intelligence",
        )

    @app.get("/trends/explorer", response_class=HTMLResponse)
    def trend_explorer(request: Request, q: str = None, domain: str = None):
        with repository_scope(request) as repos:
            # Reusing list_trends for explorer
            trends = repos["trend_profiles"].list_trends(limit=100, domain=domain)
            if q:
                q = q.lower()
                trends = [t for t in trends if q in t["title"].lower() or q in (t.get("summary") or "").lower()]

        return render(
            request,
            "pages/trends/explorer.html",
            {"trends": trends, "query": q or "", "domain": domain or ""},
            active="trends",
            title="Trend Explorer",
        )

    @app.get("/trends/graph", response_class=HTMLResponse)
    def view_trend_graph(request: Request):
        with repository_scope(request) as repos:
            data = trend_queries.trend_graph_data(repos)

        return render(
            request,
            "pages/trends/graph.html",
            data,
            active="trends",
            title="Trend Reality Graph",
        )

    @app.get("/trends/sources", response_class=HTMLResponse)
    def view_trend_sources(request: Request):
        with repository_scope(request) as repos:
            sources = trend_queries.trend_sources_page(repos)

        return render(
            request,
            "pages/trends/sources.html",
            {"sources": sources},
            active="trends",
            title="Trend Sources",
        )

    @app.get("/trends/{trend_id}", response_class=HTMLResponse)
    def view_trend(request: Request, trend_id: int):
        with repository_scope(request) as repos:
            data = trend_queries.trend_detail(repos, trend_id)

        if not data:
            raise HTTPException(status_code=404, detail="Trend not found")

        return render(
            request,
            "pages/trends/trend_detail.html",
            data,
            active="trends",
            title=data["trend"]["title"],
        )
