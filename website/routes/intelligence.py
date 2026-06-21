"""Primary intelligence consumption routes."""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, HTTPException, Request
from website.services import workbench_queries
from website.services.repository_provider import repository_scope
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

    @app.get("/trends", response_class=HTMLResponse)
    def trend_reports(
        request: Request,
        q: str = None,
        source_type: str = None,
        sort: str = "updated_desc",
        page: int = 1,
    ):
        with repository_scope(request) as repos:
            data = workbench_queries.report_list(
                repos,
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

    @app.get("/trends/{trend_id}", response_class=HTMLResponse)
    def trend_report_detail(request: Request, trend_id: int):
        with repository_scope(request) as repos:
            detail = workbench_queries.report_detail(repos, "trend", trend_id)

        if detail is None:
            raise HTTPException(status_code=404, detail="Trend report not found")

        return render(
            request,
            "pages/report_detail.html",
            detail,
            active="trends",
            title=detail["report"]["title"],
        )

    @app.get("/frictions", response_class=HTMLResponse)
    def friction_reports(
        request: Request,
        q: str = None,
        source_type: str = None,
        sort: str = "updated_desc",
        page: int = 1,
    ):
        with repository_scope(request) as repos:
            data = workbench_queries.report_list(
                repos,
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

    @app.get("/frictions/{profile_id}", response_class=HTMLResponse)
    def friction_report_detail(request: Request, profile_id: int):
        with repository_scope(request) as repos:
            detail = workbench_queries.report_detail(repos, "friction", profile_id)

        if detail is None:
            raise HTTPException(status_code=404, detail="Friction report not found")

        return render(
            request,
            "pages/report_detail.html",
            detail,
            active="frictions",
            title=detail["report"]["title"],
        )

    @app.get("/evidence", response_class=HTMLResponse)
    def evidence_index(request: Request, page: int = 1, q: str = None, source_type: str = None):
        with repository_scope(request) as repos:
            data = workbench_queries.evidence_page(
                repos,
                page_num=page,
                query=q,
                source_type=source_type,
            )

        return render(
            request,
            "pages/evidence.html",
            data,
            active="landing",
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
            active="landing",
            title=f"Evidence {evidence_id}",
        )

    @app.get("/sources", response_class=HTMLResponse)
    def sources_index(request: Request):
        with repository_scope(request) as repos:
            source_rows = workbench_queries.sources_page(repos)

        return render(
            request,
            "pages/sources.html",
            {"source_rows": source_rows},
            active="landing",
            title="Sources",
        )

    @app.get("/sources/{source_id}", response_class=HTMLResponse)
    def source_detail(request: Request, source_id: int):
        with repository_scope(request) as repos:
            detail = workbench_queries.source_detail(repos, source_id)

        if detail is None:
            raise HTTPException(status_code=404, detail="Source not found")

        return render(
            request,
            "pages/source_detail.html",
            detail,
            active="landing",
            title=f"Source {source_id}",
        )

    @app.get("/search", response_class=HTMLResponse)
    def global_search(request: Request, q: str = "", domain: str = ""):
        with repository_scope(request) as repos:
            data = workbench_queries.global_search(repos, q=q, domain=domain)

        return render(
            request,
            "pages/search.html",
            data,
            active="landing",
            title="Search",
        )
