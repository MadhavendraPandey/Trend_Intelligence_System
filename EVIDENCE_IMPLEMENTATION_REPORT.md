# Phase 6 Evidence Foundation Implementation Report

## Scope

Implemented the Phase 6 evidence foundation only.

Created:

- `evidence`
- `validation_events`

Not implemented:

- complaints
- complaint signals
- friction candidates
- frictions
- trend tables
- entity tables
- extraction logic
- AI logic
- grouping or clustering logic

## Files Created

- `database/migrations/004_evidence_foundation.sql`
- `database/repositories/evidence_repository.py`
- `database/repositories/validation_repository.py`
- `core/models/evidence.py`
- `core/models/validation_event.py`
- `EVIDENCE_IMPLEMENTATION_REPORT.md`

## Files Modified

- `database/repositories/__init__.py`
- `core/models/__init__.py`

## Schema Summary

### `evidence`

Stores atomic, verifiable observations linked to source posts.

Columns:

- `evidence_id`
- `post_id`
- `evidence_type`
- `observation`
- `source_url`
- `source_type`
- `author`
- `published_at`
- `captured_at`
- `context`
- `metadata_json`
- `created_at`

Indexes:

- `post_id`
- `evidence_type`
- `(source_type, published_at)`
- `source_url`
- `captured_at`

Foreign keys:

- `post_id` references `posts(id)` with cascade delete.

### `validation_events`

Stores human validation actions against evidence records.

Columns:

- `validation_event_id`
- `evidence_id`
- `action`
- `reason`
- `actor`
- `created_at`

Allowed actions:

- `validated`
- `rejected`
- `merged`
- `reopened`
- `needs_review`

Indexes:

- `evidence_id`
- `action`
- `created_at`

Foreign keys:

- `evidence_id` references `evidence(evidence_id)` with cascade delete.

## Repository Summary

### `EvidenceRepository`

Owns all database access for evidence records.

Implemented:

- `create_evidence`
- `get_evidence`
- `update_evidence`
- `delete_evidence`
- `list_evidence`
- `list_by_post`
- `count_evidence`

Evidence updates are limited to curation fields:

- `context`
- `metadata_json`

This preserves the original observation as the stable evidence record.

### `ValidationRepository`

Owns all database access for validation events.

Implemented:

- `create_validation_event`
- `get_validation_event`
- `update_validation_event`
- `delete_validation_event`
- `list_for_evidence`

Validation updates are limited to curation fields:

- `reason`
- `actor`

The recorded action is not changed by update operations.

## Evidence-First Alignment

- No confidence fields were added.
- No score fields were added.
- No ranking fields were added.
- Evidence records store observations, source traceability, timestamps, and context.
- Validation is represented as human event history rather than certainty.
- Evidence is stored in core database infrastructure and is not owned by Trend or Friction modules.

## Validation Results

Passed.

Checks run:

- Compile check:
  - `.venv\Scripts\python.exe -m compileall core database main.py scheduler.py`
  - Result: passed
- Smoke imports:
  - `SQLiteStorage`
  - `Evidence`
  - `ValidationEvent`
  - `EvidenceRepository`
  - `ValidationRepository`
  - Result: passed
- Migration validation:
  - Applied all migrations, including `004_evidence_foundation`, against a temporary SQLite database.
  - Verified `PRAGMA foreign_keys = ON`.
  - Verified required Phase 6 tables exist.
  - Result: passed
- Repository CRUD tests:
  - Created source and post through existing repositories.
  - Created, read, listed, curated, and deleted evidence through `EvidenceRepository`.
  - Created, read, listed, curated, and deleted validation events through `ValidationRepository`.
  - Result: passed
- Foreign key validation:
  - Invalid `evidence.post_id` was rejected.
  - Invalid `validation_events.evidence_id` was rejected.
  - Result: passed
- Validation action guard:
  - Unsupported action `confidence_score` was rejected.
  - Result: passed
- Scope validation:
  - Confirmed the Phase 6 migration did not create:
    - complaints
    - complaint signals
    - friction candidates
    - frictions
    - trends
    - trend observations
    - entities
    - topics
  - Result: passed

Notes:

- Validation used a temporary SQLite database and did not execute live
  collection, analysis, extraction, LLM, trend, or friction workflows.
