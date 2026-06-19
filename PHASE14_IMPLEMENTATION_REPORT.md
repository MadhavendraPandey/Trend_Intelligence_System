# Phase 14 Intelligence Workbench Implementation Report

## Scope

Implemented the Intelligence Workbench UI refactor and architecture cleanup.
This phase did not modify extraction, grouping, candidate generation, scoring,
report generation, or intelligence algorithms.

## Files Created

- `website/compat/__init__.py`
- `website/compat/fastapi.py`
- `website/routes/__init__.py`
- `website/routes/dashboard.py`
- `website/routes/evidence.py`
- `website/routes/groups.py`
- `website/routes/candidates.py`
- `website/routes/runs.py`
- `website/services/__init__.py`
- `website/services/repository_provider.py`
- `website/services/rendering.py`
- `website/services/workbench_queries.py`
- `website/templates/layouts/app.html`
- `website/templates/components/sidebar.html`
- `website/templates/components/topbar.html`
- `website/templates/components/card.html`
- `website/templates/components/table.html`
- `website/templates/components/badge.html`
- `website/templates/components/search.html`
- `website/templates/components/empty_state.html`
- `website/templates/pages/dashboard.html`
- `website/templates/pages/evidence.html`
- `website/templates/pages/evidence_detail.html`
- `website/templates/pages/groups.html`
- `website/templates/pages/group_detail.html`
- `website/templates/pages/candidates.html`
- `website/templates/pages/candidate_detail.html`
- `website/templates/pages/runs.html`
- `website/templates/pages/placeholder.html`
- `website/static/css/tokens.css`
- `website/static/css/layout.css`
- `website/static/css/components.css`
- `website/static/css/pages.css`
- `website/static/js/README.md`
- `website/static/assets/README.md`
- `PHASE14_IMPLEMENTATION_REPORT.md`

## Files Moved

- None.

The previous single-file dashboard was refactored in place from `website/app.py`
into route modules, services, templates, and static assets.

## Files Modified

- `website/app.py`
- `website/__init__.py`
- `website/README.md`
- `database/repositories/source_run_repository.py`
- `DASHBOARD_ARCHITECTURE.md`

## Files Removed

- `fastapi/__init__.py`
- `fastapi/responses.py`
- `fastapi/testclient.py`
- `fastapi/`

The top-level `fastapi/` shim was removed because it shadowed the third-party
package namespace. Its limited local fallback behavior now lives under
`website/compat/fastapi.py`.

## Architecture Decisions

- FastAPI remains the application server.
- Jinja remains the presentation layer.
- Route modules register pages by workbench section.
- Website services assemble read-only view data.
- Repositories continue to own database access.
- The workbench does not execute raw SQL.
- The UI remains server-rendered and avoids React, Vue, Next.js, TypeScript
  frameworks, SPA routing, and front-end build systems.
- Placeholder routes exist only for future navigation sections and do not
  implement intelligence behavior.

## UI Decisions

- Added a professional dark theme using CSS tokens.
- Split styling into tokens, layout, component, and page CSS.
- Added reusable sidebar, topbar, card, table, badge, search, metric card, and
  empty-state primitives.
- Emphasized traceability with Candidate -> Group -> Evidence -> Post and
  Post -> Evidence -> Group -> Candidate chains.
- Kept information density high with compact tables and restrained spacing.
- Added subtle hover and page-entry motion without flashy animation.

## Repository Additions

Added read-only source-run methods required by the workbench:

- `SourceRunRepository.latest_run`
- `SourceRunRepository.list_runs`
- `SourceRunRepository.count_runs`

## Validation Results

Passed.

Checks run:

- Compile:
  - `C:\Users\pande\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m compileall website database\repositories core main.py scheduler.py`
  - Result: passed
- Web boundary scan:
  - `rg -n "SELECT|INSERT|UPDATE|DELETE" website`
  - Result: passed, no raw SQL in `website/`
- FastAPI/Jinja import smoke:
  - Imported `website.app`
  - Created app through `create_app`
  - Confirmed 15 routes registered
  - Confirmed obsolete top-level `fastapi/` directory no longer exists
  - Result: passed
- Repository integration:
  - Created a temporary SQLite database
  - Seeded source, post, evidence, evidence group, candidate, and source run
    records through repositories
  - Result: passed
- Route validation:
  - `/`
  - `/evidence`
  - `/evidence/{id}`
  - `/groups`
  - `/groups/{id}`
  - `/candidates`
  - `/candidates/{id}`
  - `/runs`
  - `/sources`
  - `/posts`
  - `/validation`
  - `/decisions`
  - `/metrics`
  - `/settings`
  - `/static/css/tokens.css`
  - Result: passed
- Traceability validation:
  - Verified candidate detail renders Candidate -> Group -> Evidence -> Post
  - Verified evidence pages render evidence records
  - Result: passed

Validation note:

- The project `.venv\Scripts\python.exe` could not be executed from the
  sandbox because Windows returned `Access is denied`.
- Validation used the bundled Codex Python runtime plus the repository venv
  packages on `PYTHONPATH`.

## Constraints Honored

- No intelligence generation was added.
- No extraction logic was changed.
- No grouping logic was changed.
- No candidate generation logic was changed.
- No scoring, ranking, opportunity detection, market analysis, or business
  recommendations were added.
