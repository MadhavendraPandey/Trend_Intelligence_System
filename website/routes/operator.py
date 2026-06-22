"""Routes for the Internal Operator Console.

Purpose:
    Provide secure, internal-only operational views for system management.
    Includes database explorer, SQL studio, and health monitor.
"""

from __future__ import annotations

from website.compat.fastapi import HTMLResponse, HTTPException, Request, Form
from website.services.rendering import render
from website.services.repository_provider import repository_scope


def register_routes(app):
    """Register operator routes."""

    @app.get("/operator", response_class=HTMLResponse)
    def operator_dashboard(request: Request):
        with repository_scope(request) as repos:
            summary = repos["operator"].get_system_overview()
            orphans = repos["operator"].detect_orphans()

        return render(
            request,
            "pages/operator/dashboard.html",
            {"summary": summary, "orphans": orphans},
            active="operator",
            title="Operator Console",
        )

    @app.get("/operator/explorer", response_class=HTMLResponse)
    def database_explorer(request: Request):
        with repository_scope(request) as repos:
            tables = repos["operator"].list_tables()

        return render(
            request,
            "pages/operator/explorer.html",
            {"tables": tables},
            active="operator",
            title="Database Explorer",
        )

    @app.get("/operator/explorer/{table}", response_class=HTMLResponse)
    def table_browser(request: Request, table: str, page: int = 1):
        limit = 50
        offset = (page - 1) * limit

        with repository_scope(request) as repos:
            try:
                data = repos["operator"].paginate_table(table, limit=limit, offset=offset)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        return render(
            request,
            "pages/operator/table_browser.html",
            {
                "table": table,
                "rows": data["rows"],
                "columns": data["columns"],
                "total": data["total_count"],
                "page": page,
                "has_next": (offset + limit) < data["total_count"],
                "has_prev": page > 1
            },
            active="operator",
            title=f"Table: {table}",
        )

    @app.get("/operator/sql", response_class=HTMLResponse)
    def sql_studio(request: Request):
        with repository_scope(request) as repos:
            history = repos["operator"].get_query_history()

        return render(
            request,
            "pages/operator/sql_studio.html",
            {"history": history, "query": "", "results": None},
            active="operator",
            title="SQL Studio",
        )

    @app.post("/operator/sql", response_class=HTMLResponse)
    def execute_sql(request: Request, query: str = Form(...)):
        results = None
        error = None

        with repository_scope(request) as repos:
            try:
                results = repos["operator"].execute_operator_sql(query)
            except Exception as e:
                error = str(e)

            history = repos["operator"].get_query_history()

        return render(
            request,
            "pages/operator/sql_studio.html",
            {"history": history, "query": query, "results": results, "error": error},
            active="operator",
            title="SQL Studio",
        )

    @app.get("/operator/quality", response_class=HTMLResponse)
    def quality_dashboard(request: Request):
        with repository_scope(request) as repos:
            orphans = repos["operator"].detect_orphans()
            stats = repos["operator"].get_storage_stats()

        return render(
            request,
            "pages/operator/quality.html",
            {"orphans": orphans, "stats": stats},
            active="operator",
            title="Data Quality",
        )

    @app.get("/operator/schema", response_class=HTMLResponse)
    def schema_explorer(request: Request):
        with repository_scope(request) as repos:
            tables = repos["operator"].list_tables()
            schema = {}
            for table in tables:
                schema[table] = repos["operator"].get_table_schema(table)

        return render(
            request,
            "pages/operator/schema.html",
            {"schema": schema},
            active="operator",
            title="Schema Explorer",
        )
