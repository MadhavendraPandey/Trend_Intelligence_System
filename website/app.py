"""Application factory for the Intelligence Workbench.

Purpose:
    Create the FastAPI application that serves the read-only, server-rendered
    intelligence inspection UI.

Architecture notes:
    FastAPI remains both backend and web server. Routes render Jinja templates,
    services coordinate read-only view data, repositories own database access,
    and SQLite remains the durable source of truth.

Future extension guidance:
    Register new route modules here as workbench sections mature. Keep
    intelligence generation outside the website package.
"""

from __future__ import annotations

from pathlib import Path

from website.compat.fastapi import FastAPI, StaticFiles
from website.routes import (
    candidates,
    dashboard,
    evidence,
    groups,
    profiles,
    runs,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEBSITE_ROOT = Path(__file__).resolve().parent
DEFAULT_DB_FILE = PROJECT_ROOT / "database" / "intelligence_platform.sqlite"
DEFAULT_MIGRATIONS_DIR = PROJECT_ROOT / "database" / "migrations"


def create_app(db_file=DEFAULT_DB_FILE, migrations_dir=DEFAULT_MIGRATIONS_DIR):
    """Create and configure the read-only Intelligence Workbench app."""
    workbench = FastAPI(
        title="Intelligence Workbench",
        version="2.0.0",
    )
    workbench.state.db_file = Path(db_file)
    workbench.state.migrations_dir = Path(migrations_dir)

    workbench.mount(
        "/static",
        StaticFiles(directory=WEBSITE_ROOT / "static"),
        name="static",
    )

    dashboard.register_routes(workbench)
    evidence.register_routes(workbench)
    groups.register_routes(workbench)
    candidates.register_routes(workbench)
    profiles.register_routes(workbench)
    runs.register_routes(workbench)

    return workbench


app = create_app()
