# Database Proposal V2: Evidence-First SQLite Architecture

## Overview

SQLite should become the source of truth because the Intelligence Platform needs durable local relational storage, strong traceability, foreign keys, transaction safety, simple backups, and low operational burden. JSON remains useful only for import, export, backup, and recovery.

The revised schema stores observations, evidence, relationships, and validation events. It does not store platform opinions such as confidence, opportunity score, trend score, signal strength, candidate score, or AI certainty.

Current Trend Intelligence code still produces score-based runtime objects. Those can remain transient/report-era compatibility outputs, but the canonical database should store evidence-based facts.

## Core Relationship Diagram

```text
sources
  └─ source_runs
       └─ posts
            ├─ evidence
            ├─ post_entities
            ├─ post_topics
            ├─ trend_observations
            │    └─ trends
            │         ├─ trend_evidence
            │         └─ validation_events
            └─ complaints
                 ├─ complaint_signals
                 ├─ complaint_evidence
                 └─ friction_candidate_complaints
                      └─ friction_candidates
                           ├─ friction_candidate_evidence
                           └─ frictions
                                ├─ friction_evidence
                                ├─ friction_workarounds
                                └─ validation_events
```

## Table Design

### `sources`

Purpose: Registered collection origins.

Columns:
- `id`: primary key
- `source_type`: rss, reddit, github, hackernews, arxiv, stackoverflow, forum
- `name`: human-readable source name
- `base_url`: optional source root
- `owner_module`: trend, friction, shared, or future module name
- `is_active`: operational flag
- `created_at`, `updated_at`

Indexes:
- unique `(source_type, name)`
- index `owner_module`

Relationships:
- one source has many `source_runs`
- one source has many `posts`

### `source_runs`

Purpose: Trace collection activity without mixing operational metrics into intelligence outputs.

Columns:
- `id`: primary key
- `source_id`: foreign key to `sources`
- `started_at`
- `finished_at`
- `status`
- `items_seen`
- `items_stored`
- `duplicates_seen`
- `errors_seen`
- `run_notes`
- `metadata_json`

Indexes:
- `(source_id, started_at)`
- `status`

Relationships:
- one run has many `posts`

### `posts`

Purpose: Canonical normalized observation unit.

Columns:
- `id`: primary key
- `source_id`: foreign key to `sources`
- `source_run_id`: nullable foreign key to `source_runs`
- `source_type`
- `source_record_id`: external id when available
- `url`
- `canonical_url`
- `title`
- `content`
- `author`
- `published_at`
- `captured_at`
- `content_hash`
- `language`
- `raw_json`
- `metadata_json`
- `created_at`, `updated_at`

Indexes:
- unique `canonical_url` when present
- unique `content_hash` when present
- `(source_type, published_at)`
- `(source_id, captured_at)`

Relationships:
- one post has many evidence records, topics, entities, trend observations, and complaints

### `evidence`

Purpose: First-class traceable excerpt, observation, or artifact.

Columns:
- `id`: primary key
- `post_id`: nullable foreign key to `posts`
- `source_id`: nullable foreign key to `sources`
- `source_type`
- `source_url`
- `author`
- `quote`
- `context`
- `evidence_kind`: quote, link, metric, comment, repository_metadata, paper_metadata, manual_note
- `captured_at`
- `published_at`
- `metadata_json`
- `created_at`

Indexes:
- `post_id`
- `(source_type, published_at)`
- `source_url`
- `evidence_kind`

Relationships:
- evidence can support trends, complaints, friction candidates, and validated frictions through join tables

### `entities`

Purpose: Reusable named things observed in posts or evidence.

Columns:
- `id`: primary key
- `name`
- `entity_type`: product, company, framework, technology, person, vulnerability, repository, paper
- `canonical_name`
- `metadata_json`
- `created_at`, `updated_at`

Indexes:
- unique `(entity_type, canonical_name)`
- `name`

Relationships:
- entities connect to posts through `post_entities`

### `post_entities`

Purpose: Relationship between posts and observed entities.

Columns:
- `post_id`: foreign key to `posts`
- `entity_id`: foreign key to `entities`
- `observed_text`
- `created_at`

Primary key:
- `(post_id, entity_id, observed_text)`

### `topics`

Purpose: Controlled or discovered topic labels.

Columns:
- `id`: primary key
- `name`
- `domain`
- `theme`
- `description`
- `created_at`, `updated_at`

Indexes:
- unique `name`
- `(domain, theme)`

### `post_topics`

Purpose: Evidence-based topic occurrence, not score.

Columns:
- `post_id`: foreign key to `posts`
- `topic_id`: foreign key to `topics`
- `matched_text`
- `match_method`: alias, manual, extractor, import
- `created_at`

Primary key:
- `(post_id, topic_id, matched_text)`

### `trends`

Purpose: Persistent grouping of repeated observations across time and sources.

Columns:
- `id`: primary key
- `topic_id`: nullable foreign key to `topics`
- `name`
- `description`
- `first_seen`
- `last_seen`
- `source_count`
- `supporting_post_count`
- `evidence_count`
- `active_window_start`
- `active_window_end`
- `status`: observed, monitoring, validated, archived
- `created_at`, `updated_at`
- `metadata_json`

Indexes:
- `topic_id`
- `status`
- `(first_seen, last_seen)`
- `supporting_post_count`
- `evidence_count`

No scores, confidence, ranks, or trend levels are stored.

### `trend_observations`

Purpose: Individual post-level observations that support a trend.

Columns:
- `id`: primary key
- `trend_id`: foreign key to `trends`
- `post_id`: foreign key to `posts`
- `topic_id`: nullable foreign key to `topics`
- `observed_at`
- `observation_type`: article, repository, discussion, paper, comment, manual
- `observed_text`
- `created_at`

Indexes:
- `(trend_id, observed_at)`
- `post_id`
- `topic_id`

### `trend_evidence`

Purpose: Many-to-many link between trends and evidence.

Columns:
- `trend_id`: foreign key to `trends`
- `evidence_id`: foreign key to `evidence`
- `relationship_type`: supports, contradicts, contextualizes
- `created_at`

Primary key:
- `(trend_id, evidence_id, relationship_type)`

### `complaints`

Purpose: Atomic user/problem observation extracted or manually recorded from posts.

Columns:
- `id`: primary key
- `post_id`: foreign key to `posts`
- `complaint_text`
- `subject`
- `problem_area`
- `observed_at`
- `status`: observed, grouped, reviewed, dismissed
- `created_by`: extractor, import, manual
- `created_at`, `updated_at`
- `metadata_json`

Indexes:
- `post_id`
- `subject`
- `problem_area`
- `status`
- `observed_at`

No severity score or confidence score is stored.

### `complaint_signals`

Purpose: Observable complaint attributes useful for grouping.

Columns:
- `id`: primary key
- `complaint_id`: foreign key to `complaints`
- `signal_type`: workaround, broken_workflow, repeated_question, bug_report, churn_language, manual_tag
- `signal_value`
- `observed_text`
- `created_at`

Indexes:
- `complaint_id`
- `(signal_type, signal_value)`

### `complaint_evidence`

Purpose: Link complaints to supporting evidence.

Columns:
- `complaint_id`: foreign key to `complaints`
- `evidence_id`: foreign key to `evidence`
- `relationship_type`: supports, contradicts, context
- `created_at`

Primary key:
- `(complaint_id, evidence_id, relationship_type)`

### `friction_candidates`

Purpose: Grouped pattern of complaints before human validation.

Columns:
- `id`: primary key
- `title`
- `description`
- `problem_area`
- `first_seen`
- `last_seen`
- `complaint_count`
- `supporting_post_count`
- `evidence_count`
- `workaround_count`
- `status`: candidate, under_review, merged, dismissed, promoted
- `created_at`, `updated_at`
- `metadata_json`

Indexes:
- `problem_area`
- `status`
- `(first_seen, last_seen)`
- `complaint_count`
- `evidence_count`

No candidate score is stored.

### `friction_candidate_complaints`

Purpose: Many-to-many grouping between candidates and complaints.

Columns:
- `friction_candidate_id`: foreign key to `friction_candidates`
- `complaint_id`: foreign key to `complaints`
- `relationship_type`: primary, related, duplicate, weak_match
- `added_at`

Primary key:
- `(friction_candidate_id, complaint_id)`

### `friction_candidate_evidence`

Purpose: Link candidates to evidence.

Columns:
- `friction_candidate_id`: foreign key to `friction_candidates`
- `evidence_id`: foreign key to `evidence`
- `relationship_type`: supports, contradicts, context
- `created_at`

Primary key:
- `(friction_candidate_id, evidence_id, relationship_type)`

### `frictions`

Purpose: Human-validated persistent friction pattern.

Columns:
- `id`: primary key
- `friction_candidate_id`: nullable foreign key to `friction_candidates`
- `title`
- `description`
- `problem_area`
- `first_seen`
- `last_seen`
- `validated_at`
- `validation_state`: validated, invalidated, needs_more_evidence, archived
- `validation_count`
- `supporting_complaint_count`
- `supporting_post_count`
- `evidence_count`
- `created_at`, `updated_at`
- `metadata_json`

Indexes:
- `validation_state`
- `problem_area`
- `(first_seen, last_seen)`
- `evidence_count`

No friction score is stored.

### `friction_evidence`

Purpose: Link validated frictions to evidence.

Columns:
- `friction_id`: foreign key to `frictions`
- `evidence_id`: foreign key to `evidence`
- `relationship_type`: supports, contradicts, context
- `created_at`

Primary key:
- `(friction_id, evidence_id, relationship_type)`

### `friction_workarounds`

Purpose: Observable workaround patterns associated with frictions.

Columns:
- `id`: primary key
- `friction_id`: foreign key to `frictions`
- `post_id`: nullable foreign key to `posts`
- `evidence_id`: nullable foreign key to `evidence`
- `workaround_text`
- `observed_at`
- `created_at`

Indexes:
- `friction_id`
- `observed_at`

### `validation_events`

Purpose: Record human validation as events, not confidence scores.

Columns:
- `id`: primary key
- `target_type`: trend, friction, complaint, friction_candidate, evidence
- `target_id`
- `event_type`: validated, rejected, needs_more_evidence, merged, split, archived, reopened
- `validator`
- `validated_at`
- `rationale`
- `evidence_snapshot_json`
- `created_at`

Indexes:
- `(target_type, target_id)`
- `event_type`
- `validated_at`

### `reports`

Purpose: Preserve generated report snapshots and trace their source run.

Columns:
- `id`: primary key
- `module_name`
- `report_type`
- `generated_at`
- `period_start`
- `period_end`
- `title`
- `content_path`
- `json_path`
- `metadata_json`

Indexes:
- `(module_name, generated_at)`
- `report_type`

## Repository Review

Recommended repositories:
- `SourceRepository`: sources and source runs.
- `PostRepository`: canonical post persistence, dedupe, JSON import/export.
- `EvidenceRepository`: evidence creation, lookup, and target linking.
- `TopicRepository`: topics, post-topic occurrences, entities.
- `TrendRepository`: trends, trend observations, trend evidence, trend validations.
- `ComplaintRepository`: complaints, complaint signals, complaint evidence.
- `FrictionRepository`: candidates, complaint grouping, validated frictions, workarounds, validation events.
- `ReportRepository`: report metadata and generated artifact tracking.

Reports and engines should consume repositories, not raw SQL.

## Source Layer Review

Add source metadata tables because evidence-first traceability requires collection lineage. `sources` and `source_runs` are justified because they answer:
- where did this post come from?
- when was it captured?
- was it part of a successful or partial run?
- how healthy is a source over time?

Avoid `source_health` for now. Health can be derived from `source_runs` until operational needs justify a separate table.

## Compatibility Note

Existing Trend Intelligence runtime scoring can remain in code for backward-compatible reports, but canonical SQLite storage should not persist those score fields as platform truth. If legacy reports must be archived, store them as report snapshots in `reports.metadata_json` or external JSON files, clearly marked as generated artifacts rather than canonical evidence.
