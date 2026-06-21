"""Template rendering helpers for the Intelligence Workbench."""

from __future__ import annotations

from pathlib import Path

from website.compat.fastapi import Jinja2Templates


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_ROOT))


def render(request, template_name, context=None, active="dashboard", title=None):
    """Render a Jinja template with workbench defaults."""
    page_context = {
        "request": request,
        "active_nav": active,
        "page_title": title or "Intelligence Workbench",
        "app_name": "Intelligence Workbench",
    }
    if context:
        page_context.update(context)

    # Use explicit keyword arguments for compatibility across FastAPI/Starlette versions
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=page_context
    )
