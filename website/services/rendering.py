"""Template rendering helpers for the Intelligence Workbench.

Purpose:
    Provide one configured Jinja template environment and consistent context
    defaults for all server-rendered pages.

Architecture notes:
    Templates live under `website/templates`. Rendering helpers add active
    navigation state and application labels, but no intelligence behavior.

Future extension guidance:
    Add global filters or presentation-only helpers here as the design system
    matures.
"""

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

    try:
        return templates.TemplateResponse(request, template_name, page_context)
    except TypeError:
        return templates.TemplateResponse(template_name, page_context)
