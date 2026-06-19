# Phase 12 Candidate Friction Generation Report

## Scope

Implemented Candidate Friction generation from Evidence Groups.

Output:

```text
Evidence Groups
  -> Candidate Frictions
```

Candidate frictions are generated hypotheses only.

## Files Created

- `database/migrations/006_friction_candidates.sql`
- `database/repositories/friction_candidate_repository.py`
- `core/models/friction_candidate.py`
- `modules/friction/services/friction_candidate_generation_service.py`
- `FRICTION_CANDIDATE_ARCHITECTURE.md`
- `PHASE12_IMPLEMENTATION_REPORT.md`

## Files Modified

- `database/repositories/__init__.py`
- `core/models/__init__.py`
- `modules/friction/services/__init__.py`

## Schema Summary

### `friction_candidates`

Fields:

- `id`
- `title`
- `description`
- `status`
- `created_at`
- `updated_at`
- `metadata_json`

Allowed statuses:

- `generated`
- `reviewed`
- `accepted`
- `rejected`

### `friction_candidate_groups`

Fields:

- `friction_candidate_id`
- `evidence_group_id`

## Repository Summary

`FrictionCandidateRepository` owns candidate persistence and evidence group
links.

Implemented:

- `create_candidate`
- `get_candidate`
- `update_candidate`
- `delete_candidate`
- `list_candidates`
- `add_group`
- `get_group_link`
- `remove_group`
- `list_groups`
- `list_candidates_for_group`
- `count_candidates`
- `count_group_links`

## Service Summary

`FrictionCandidateGenerationService`:

- reads evidence groups through `EvidenceGroupRepository`
- uses the existing `LLMProvider` architecture
- validates strict JSON responses
- persists candidates through `FrictionCandidateRepository`
- persists evidence group links through `friction_candidate_groups`
- supports batch generation
- supports regeneration without deleting previous candidates
- adds generation metadata

## Explicitly Not Implemented

- Validated Frictions
- Opportunity Detection
- Market Analysis
- Startup Recommendations
- Revenue Estimation
- Prioritization
- Scoring
- Ranking

## Validation Results

Passed.

Checks run:

- Compile check:
  - `.venv\Scripts\python.exe -m compileall core database modules main.py scheduler.py`
  - Result: passed
- Repository integration:
  - Created a temporary SQLite database.
  - Created evidence groups through `EvidenceGroupRepository`.
  - Generated candidate frictions with a fake `LLMProvider`.
  - Persisted candidates through `FrictionCandidateRepository`.
  - Result: passed
- Temporary SQLite validation:
  - Applied all migrations through `SQLiteStorage`.
  - Verified `006_friction_candidates` was recorded in `schema_migrations`.
  - Verified foreign keys are enabled.
  - Result: passed
- JSON schema validation:
  - Valid candidate JSON was accepted.
  - Non-JSON response was rejected.
  - Non-object root was rejected.
  - Missing `candidates` list was rejected.
  - Missing candidate title was rejected.
  - Missing candidate description was rejected.
  - Empty supporting evidence group ids were rejected.
  - Non-integer supporting evidence group ids were rejected.
  - Supporting group ids outside the current batch were rejected.
  - Result: passed
- Candidate persistence tests:
  - Created generated candidates.
  - Verified candidate status defaults to `generated`.
  - Updated candidate status to `reviewed`.
  - Rejected unsupported status `validated`.
  - Stored generation metadata:
    - `model_name`
    - `provider_name`
    - `generation_version`
    - `generation_method`
    - `created_at`
    - `generation_run_id`
    - `regeneration`
    - `supporting_evidence_group_ids`
  - Result: passed
- Evidence group linkage tests:
  - Linked candidates to supporting evidence groups.
  - Verified duplicate links remain single rows.
  - Listed groups for a candidate.
  - Listed candidates for an evidence group.
  - Invalid candidate foreign key was rejected.
  - Invalid evidence group foreign key was rejected.
  - Result: passed
- Regeneration tests:
  - Created additional candidates from selected groups.
  - Verified regeneration did not delete previous candidates.
  - Result: passed
- Retry handling:
  - Malformed first response followed by valid response succeeded with retry.
  - Result: passed
- Boundary scan:
  - No Validated Frictions, Opportunity Detection, Market Analysis, Startup
    Recommendations, Revenue Estimation, Prioritization, Scoring, or Ranking
    was implemented.
  - Raw SQL appears only inside the repository layer.
  - Result: passed

Notes:

- Validation used a temporary SQLite database and fake LLM provider.
- No live model call, network call, validated friction workflow, opportunity
  workflow, market analysis, recommendation, revenue estimation,
  prioritization, scoring, or ranking workflow was executed.
