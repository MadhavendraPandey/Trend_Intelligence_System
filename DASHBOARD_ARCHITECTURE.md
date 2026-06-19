# Intelligence Workbench Architecture

## Purpose

Phase 14 refactors the Phase 13 dashboard into a maintainable read-only
Intelligence Workbench.

The workbench exists so a human can inspect:

- Posts
- Evidence
- Evidence Groups
- Candidate Frictions
- Source runs

without changing intelligence logic.

## Application

The workbench is a server-rendered FastAPI application under `website/`.

```text
Browser
  -> FastAPI Routes
  -> Jinja Templates
  -> Website Services
  -> Repositories
  -> SQLite
```

FastAPI remains both backend application and web server. Jinja templates remain
the presentation layer. No SPA framework, front-end build system, or API-first
front-end architecture was introduced.

## Structure

```text
website/
  app.py
  compat/
  routes/
    dashboard.py
    evidence.py
    groups.py
    candidates.py
    runs.py
  services/
    repository_provider.py
    rendering.py
    workbench_queries.py
  templates/
    layouts/
      app.html
    components/
      sidebar.html
      topbar.html
      card.html
      table.html
      badge.html
      search.html
      empty_state.html
    pages/
      dashboard.html
      evidence.html
      evidence_detail.html
      groups.html
      group_detail.html
      candidates.html
      candidate_detail.html
      runs.html
      placeholder.html
  static/
    css/
      tokens.css
      layout.css
      components.css
      pages.css
    js/
    assets/
```

## Routes

Implemented inspection routes:

- `/`
- `/evidence`
- `/evidence/{id}`
- `/groups`
- `/groups/{id}`
- `/candidates`
- `/candidates/{id}`
- `/runs`

Reserved future navigation routes:

- `/sources`
- `/posts`
- `/validation`
- `/decisions`
- `/metrics`
- `/settings`

## Read-Only Rules

The workbench:

- reads through repositories
- never writes intelligence data
- never creates intelligence objects
- never performs validation actions
- never scores or ranks
- never generates opportunities
- never makes recommendations

## Design System

The UI uses a dark operational workbench design language optimized for:

- dense data inspection
- traceability
- readable tables
- restrained motion
- border-first surface hierarchy
- reusable components

Reusable primitives include:

- sidebar
- topbar
- metric card
- panel/card
- table
- badge
- search
- empty state

## Metrics

Dashboard summary metrics:

- total posts
- total evidence
- total groups
- total candidates
- latest run

## Traceability

The dashboard makes the chain visible:

```text
Candidate
  -> Group
  -> Evidence
  -> Post
```

This chain appears in candidate detail, group detail, and evidence detail
pages.

## Explorer Pages

### Evidence Explorer

- list evidence
- pagination
- search observation text

### Evidence Detail

- evidence record
- source post
- metadata

### Group Explorer

- list groups
- member counts

### Group Detail

- group
- all member evidence

### Candidate Explorer

- list candidates
- status

### Candidate Detail

- candidate
- linked groups
- linked evidence

## Future Extension Guidance

Keep this package read-only until a future phase explicitly introduces review
or validation workflows. Future pages should add route modules, services, and
templates without moving intelligence generation into the web layer.
