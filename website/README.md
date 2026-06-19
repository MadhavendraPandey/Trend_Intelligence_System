# Intelligence Workbench

Read-only FastAPI and Jinja workbench for inspecting platform intelligence
artifacts.

## Architecture

```text
Browser
  -> FastAPI routes
  -> Jinja templates
  -> Website services
  -> Repositories
  -> SQLite
```

## Structure

- `app.py`: application factory and route registration
- `routes/`: HTTP route modules by workbench section
- `services/`: read-only view-model assembly
- `templates/layouts/`: shared Jinja page layouts
- `templates/components/`: reusable UI primitives
- `templates/pages/`: page templates
- `static/css/`: design tokens, layout, components, and page styles
- `compat/`: local fallback for lightweight environments without FastAPI

## Run

Run from the repository root:

```bash
uvicorn website.app:app --reload
```

The app is read-only. It does not run extraction, grouping, candidate
generation, validation, scoring, or reports.
