# Phase 11 LLM Evidence Grouping Report

## Scope

Implemented LLM-powered Evidence -> Theme Groups.

This phase creates theme groups only. It does not create frictions, complaints,
opportunities, scores, rankings, recommendations, or market validation.

## Files Created

- `modules/friction/services/llm_evidence_grouping_service.py`
- `LLM_EVIDENCE_GROUPING_ARCHITECTURE.md`
- `PHASE11_IMPLEMENTATION_REPORT.md`

## Files Modified

- `modules/friction/services/__init__.py`

## Service Summary

`LLMEvidenceGroupingService`:

- reads evidence through `EvidenceRepository`
- reads existing membership state through `EvidenceGroupRepository`
- calls an `LLMProvider`
- validates strict JSON responses
- persists theme groups through `EvidenceGroupRepository`
- persists memberships through `evidence_group_members`
- supports batch grouping
- supports regrouping without deleting evidence or existing groups

## Group Output

Each LLM group must contain:

- `title`
- `description`
- `supporting_evidence_ids`

Each persisted group is traceable through its member evidence records.

## Grouping Metadata

Each group stores:

- `model_name`
- `provider_name`
- `grouping_version`
- `created_at`
- `grouping_method`
- `grouping_run_id`
- `regrouping`
- `supporting_evidence_ids`

## Structured JSON Validation

Rejected responses include:

- non-JSON text
- non-object roots
- missing `groups`
- non-list `groups`
- missing title
- missing description
- empty supporting evidence ids
- non-integer supporting evidence ids
- supporting evidence ids outside the current batch

## Validation Results

Passed.

Checks run:

- Compile check:
  - `.venv\Scripts\python.exe -m compileall modules\friction\services core database modules main.py scheduler.py`
  - Result: passed
- Repository integration:
  - Created a temporary SQLite database.
  - Created source, post, and evidence records through repositories.
  - Ran `LLMEvidenceGroupingService` with a fake `LLMProvider`.
  - Result: passed
- Temporary SQLite validation:
  - Applied existing migrations through `SQLiteStorage`.
  - Persisted groups through `EvidenceGroupRepository`.
  - Persisted memberships through `evidence_group_members`.
  - Result: passed
- JSON schema validation:
  - Valid theme-group JSON was accepted.
  - Non-JSON response was rejected.
  - Non-object root was rejected.
  - Missing `groups` list was rejected.
  - Missing title was rejected.
  - Missing description was rejected.
  - Empty supporting evidence ids were rejected.
  - Non-integer supporting evidence ids were rejected.
  - Evidence ids outside the current batch were rejected.
  - Result: passed
- Group persistence tests:
  - Created theme groups with title and description.
  - Stored grouping metadata:
    - `model_name`
    - `provider_name`
    - `grouping_version`
    - `created_at`
    - `grouping_method`
    - `grouping_run_id`
    - `regrouping`
    - `supporting_evidence_ids`
  - Result: passed
- Evidence membership tests:
  - Verified every created group had supporting evidence membership rows.
  - Verified ungrouped mode skips already grouped evidence.
  - Result: passed
- Regrouping tests:
  - Created additional groups for selected evidence.
  - Verified regrouping did not delete evidence.
  - Verified regrouping did not delete existing groups.
  - Result: passed
- Retry handling:
  - Malformed first response followed by valid response succeeded with retry.
  - Result: passed
- Boundary scan:
  - No raw SQL was added to the service.
  - No Friction Intelligence, Complaint Intelligence, Opportunity Detection,
    scoring, rankings, business recommendations, market validation, or
    candidate generation was added.
  - Result: passed

Notes:

- Validation used a temporary SQLite database and fake LLM provider.
- No live model call, network call, extraction job, friction workflow,
  complaint workflow, opportunity workflow, report generation, scoring,
  ranking, recommendation, or market validation workflow was executed.
