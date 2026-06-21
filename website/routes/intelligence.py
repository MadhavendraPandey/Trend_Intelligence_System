"""Primary intelligence consumption routes."""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, HTTPException, Request
from website.services import mock_queries as workbench_queries
from website.services.rendering import render


def register_routes(app):
    @app.get("/", response_class=HTMLResponse)
    def landing_page(request: Request):
        cards = workbench_queries.landing_cards()
        return render(
            request,
            "pages/landing.html",
            {"cards": cards},
            active="landing",
            title="Intelligence Platform",
        )

    @app.get("/trend/reports", response_class=HTMLResponse)
    def trend_reports(
        request: Request,
        q: str = None,
        source_type: str = None,
        sort: str = "updated_desc",
        page: int = 1,
    ):
        data = workbench_queries.report_list(
            domain="trend",
            q=q,
            source_type=source_type,
            sort=sort,
            page=page,
        )

        return render(
            request,
            "pages/report_list.html",
            data,
            active="trends",
            title="Trend Intelligence",
        )

    @app.get("/friction/reports", response_class=HTMLResponse)
    def friction_reports(
        request: Request,
        q: str = None,
        source_type: str = None,
        sort: str = "updated_desc",
        page: int = 1,
    ):
        data = workbench_queries.report_list(
            domain="friction",
            q=q,
            source_type=source_type,
            sort=sort,
            page=page,
        )

        return render(
            request,
            "pages/report_list.html",
            data,
            active="frictions",
            title="Friction Intelligence",
        )

    @app.get("/report/{id}", response_class=HTMLResponse)
    def unified_report_detail(request: Request, id: int):
        # In mock mode, we'll try to find it in either domain
        # For simplicity, we just use friction as a default mock
        detail = workbench_queries.report_detail("friction", id)

        if detail is None:
            raise HTTPException(status_code=404, detail="Report not found")

        return render(
            request,
            "pages/report_detail.html",
            detail,
            active="landing",
            title=detail["report"]["title"],
        )

    @app.get("/evidence/{evidence_id}", response_class=HTMLResponse)
    def evidence_detail(request: Request, evidence_id: int):
        detail = workbench_queries.evidence_detail(evidence_id)

        if detail["evidence"] is None:
            raise HTTPException(status_code=404, detail="Evidence not found")

        return render(
            request,
            "pages/evidence_detail.html",
            detail,
            active="landing",
            title=f"Evidence {evidence_id}",
        )

    @app.get("/source/{source_id}", response_class=HTMLResponse)
    def source_detail(request: Request, source_id: int):
        detail = workbench_queries.source_detail(source_id)

        if detail is None:
            raise HTTPException(status_code=404, detail="Source not found")

        return render(
            request,
            "pages/source_detail.html",
            detail,
            active="landing",
            title=f"Source {source_id}",
        )
