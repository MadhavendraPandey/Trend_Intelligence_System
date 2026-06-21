"""Routes for the Internal Operator Console."""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, Request
from website.services.rendering import render
from website.services import mock_queries


def register_routes(app):
    """Register operator routes."""

    @app.get("/operator", response_class=HTMLResponse)
    def operator_dashboard(request: Request):
        data = mock_queries.operator_summary()

        return render(
            request,
            "pages/operator/dashboard.html",
            data,
            active="operator",
            title="Operator Console",
        )
