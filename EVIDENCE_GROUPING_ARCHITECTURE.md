# Evidence Grouping Architecture

## Purpose

Phase 10 creates the Evidence Group foundation.

The architecture is:

```text
Evidence
  -> Evidence Groups
```

Evidence groups store collections of related evidence records. They do not
represent complaints, frictions, candidates, opportunities, recommendations,
scores, rankings, or business conclusions.

## Database Tables

### `evidence_groups`

Stores named evidence collections.

Fields:

- `id`
- `title`
- `description`
- `status`
- `created_at`
- `updated_at`
- `metadata_json`

### `evidence_group_members`

Stores many-to-many membership links between evidence groups and evidence
records.

Fields:

- `group_id`
- `evidence_id`

Foreign keys:

- `group_id` references `evidence_groups(id)`
- `evidence_id` references `evidence(evidence_id)`

## Repository

`EvidenceGroupRepository` owns all database access for:

- group creation
- group lookup
- group updates
- group deletion
- group listing
- membership creation
- membership lookup
- membership deletion
- membership listing

Modules and services should call this repository instead of executing raw SQL.

## Models

Core models:

- `EvidenceGroup`
- `EvidenceGroupMember`

These are data contracts only. They do not perform grouping or interpretation.

## Services

Service interfaces:

- `BaseEvidenceGroupingService`
- `EvidenceGroupingService`

The concrete service is intentionally thin. It only persists explicit
caller-supplied groups and memberships.

## Explicit Non-Goals

Phase 10 does not implement:

- Friction Intelligence
- Complaint Intelligence
- candidate generation
- opportunity detection
- recommendations
- scores
- rankings
- extraction logic
- grouping algorithms
- LLM grouping
- clustering
- semantic similarity
- embeddings

## Future Extension Guidance

Future phases may add grouping strategies that propose memberships. Those
strategies should remain outside the repository layer and should pass explicit
membership decisions into `EvidenceGroupRepository`.

No future grouping strategy should overwrite the original evidence records.
