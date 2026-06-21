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

    @app.get("/operator/explorer/{table}/{row_id}", response_class=HTMLResponse)
    def record_inspector(request: Request, table: str, row_id: str):
        # We use str for row_id because some tables might use non-int IDs (though unlikely here)
        with repository_scope(request) as repos:
            # Determine ID column (most use 'id', evidence uses 'evidence_id')
            id_col = "evidence_id" if table == "evidence" else "id"

            try:
                row = repos["operator"].get_row(table, row_id, id_col=id_col)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

            if not row:
                raise HTTPException(status_code=404, detail="Record not found")

            # Basic automated relationship discovery for the inspector
            relationships = []
            columns = repos["operator"].get_table_schema(table)
            for col in columns:
                val = row.get(col["name"])
                if col["name"].endswith("_id") and val:
                    # Potential foreign key
                    target_table = col["name"][:-3]
                    # Handle plurals or special names
                    if target_table == "post": target_table = "posts"
                    if target_table == "source": target_table = "sources"
                    if target_table == "group": target_table = "evidence_groups"

                    if target_table in repos["operator"].list_tables():
                        relationships.append({
                            "column": col["name"],
                            "table": target_table,
                            "id": val
                        })

        return render(
            request,
            "pages/operator/record_detail.html",
            {
                "table": table,
                "row": row,
                "row_id": row_id,
                "relationships": relationships
            },
            active="operator",
            title=f"Inspect: {table} #{row_id}",
        )

    @app.get("/operator/pipeline", response_class=HTMLResponse)
    def pipeline_monitor(request: Request):
        with repository_scope(request) as repos:
            runs = repos["runs"].list_runs(limit=100)

        return render(
            request,
            "pages/operator/pipeline_monitor.html",
            {"runs": runs},
            active="operator",
            title="Pipeline Monitor",
        )
