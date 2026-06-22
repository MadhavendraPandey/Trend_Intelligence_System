"""Primary intelligence consumption routes."""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, HTTPException, Request
from website.services import workbench_queries, trend_report_loader, friction_report_loader
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

    @app.get("/trend/reports", response_class=HTMLResponse)
    def trend_reports(
        request: Request,
        q: str = None,
        source_type: str = None,
        sort: str = "updated_desc",
        page: int = 1,
    ):
        report_data = trend_report_loader.load_latest_report()

        rows = []
        if report_data:
            for trend in report_data.get("top_trends", []):
                rows.append({
                    "report": {
                        "id": f"trend-{trend['rank']}",
                        "title": trend["topic"],
                    },
                    "summary": f"{trend['theme']} in {trend['domain']}",
                    "evidence_count": trend.get("mentions", 0),
                    "source_count": trend.get("source_count", 0),
                    "last_updated": report_data.get("generated_at"),
                    "report_type": "Trend",
                    "trend_data": trend
                })

        data = {
            "rows": rows,
            "page": 1,
            "total": len(rows),
            "previous_page": None,
            "next_page": None,
            "query": q or "",
            "source_type": source_type or "",
            "sort": sort,
            "report_type": "Trend",
            "signals": report_data.get("top_signals", []) if report_data else []
        }

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
        report_data = friction_report_loader.load_latest_report()

        rows = []
        if report_data:
            for friction in report_data.get("top_frictions", []):
                rows.append({
                    "report": {
                        "id": f"friction-{friction['id']}",
                        "title": friction["title"],
                    },
                    "summary": friction["validation_summary"],
                    "evidence_count": friction["evidence_count"],
                    "source_count": friction["source_count"],
                    "last_updated": friction["updated_at"],
                    "report_type": "Friction",
                    "friction_data": friction
                })

        data = {
            "rows": rows,
            "page": 1,
            "total": len(rows),
            "previous_page": None,
            "next_page": None,
            "query": q or "",
            "source_type": source_type or "",
            "sort": sort,
            "report_type": "Friction",
            "overview": report_data.get("overview") if report_data else {}
        }

        return render(
            request,
            "pages/report_list.html",
            data,
            active="frictions",
            title="Friction Intelligence",
        )

    @app.get("/report/{id}", response_class=HTMLResponse)
    def unified_report_detail(request: Request, id: str):
        if id.startswith("trend-"):
            rank = int(id.replace("trend-", ""))
            report_data = trend_report_loader.load_latest_report()
            if not report_data:
                raise HTTPException(status_code=404, detail="Trend report not found")

            trend = next((t for t in report_data.get("top_trends", []) if t["rank"] == rank), None)
            if not trend:
                raise HTTPException(status_code=404, detail="Trend not found")

            detail = {
                "report": {
                    "id": id,
                    "title": trend["topic"],
                },
                "report_type": "Trend",
                "executive_summary": f"Emerging trend in {trend['domain']}: {trend['theme']}",
                "description": f"Detailed analysis of {trend['topic']}. Trend level: {trend['trend_level']}. Confidence: {trend['confidence']}.",
                "evidence_count": trend.get("mentions", 0),
                "source_count": trend.get("source_count", 0),
                "created_at": report_data.get("generated_at"),
                "updated_at": report_data.get("generated_at"),
                "evidence_items": [],
                "sources": [],
                "trend": trend
            }
        elif id.startswith("friction-"):
            fid = int(id.replace("friction-", ""))
            report_data = friction_report_loader.load_latest_report()
            if not report_data:
                raise HTTPException(status_code=404, detail="Friction report not found")

            friction = next((f for f in report_data.get("top_frictions", []) if f["id"] == fid), None)
            if not friction:
                raise HTTPException(status_code=404, detail="Friction not found")

            detail = {
                "report": {
                    "id": id,
                    "title": friction["title"],
                },
                "report_type": "Friction",
                "executive_summary": friction["validation_summary"],
                "description": friction.get("description") or "",
                "evidence_count": friction["evidence_count"],
                "source_count": friction["source_count"],
                "created_at": friction.get("created_at") or friction["updated_at"],
                "updated_at": friction["updated_at"],
                "evidence_items": friction.get("supporting_evidence", []),
                "sources": [],
                "friction": friction
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid report ID format")

        return render(
            request,
            "pages/report_detail.html",
            detail,
            active="trends" if id.startswith("trend-") else "frictions",
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
            active="frictions",
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
            active="frictions",
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
            active="frictions",
            title="Sources",
        )

    @app.get("/source/{source_id}", response_class=HTMLResponse)
    def source_detail(request: Request, source_id: int):
        with repository_scope(request) as repos:
            detail = workbench_queries.source_detail(repos, source_id)

        if detail is None:
            raise HTTPException(status_code=404, detail="Source not found")

        return render(
            request,
            "pages/source_detail.html",
            detail,
            active="frictions",
            title=f"Source {source_id}",
        )
