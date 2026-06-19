# Phase 3 Audit

## Scope

Reviewed Phase 3 against:

- `SQLiteStorage`
- `SourceRepository`
- `PostRepository`
- `database/migrate_articles_json.py`
- `database/migrations/001_initial_schema.sql`
- `database/migrations/002_post_json_migration_fields.sql`
- current Trend pipeline entry points and report path
- `DATABASE_PROPOSAL_V2.md`

This audit did not modify implementation files.

## Executive Summary

Phase 3 successfully migrated `articles.json` into SQLite `posts` without creating trends, complaints, evidence, frictions, or friction candidates.

Read-only validation shows:

- Trend report pipeline still reads and computes successfully.
- SQLite contains 1,145 posts, matching the current JSON article count.
- URL uniqueness is preserved in the migrated SQLite copy.
- The database contains only Phase 1/3 tables: `posts`, `schema_migrations`, `source_runs`, `sources`.

However, Phase 3 is still a transitional migration, not a completed database cutover:

- The active Trend pipeline still reads `articles.json`.
- Analyzer, reporter, collectors, and weekly brief still use JSON utilities instead of repositories.
- The migration utility performs direct SQL validation queries outside repositories.
- The implemented schema is only a subset of `DATABASE_PROPOSAL_V2.md`.
- Legacy opinion fields are preserved in `analysis_json`, `filter_data_json`, and `raw_json`; this is acceptable for historical preservation but must not become canonical evidence-first truth.

## Validation Results

### Trend Pipeline Read Validation

Command run:

```text
.venv\Scripts\python.exe -c "import reporter; data=reporter.build_report_data(); ..."
```

Result:

- `total_articles`: 1145
- `analyzed_articles`: 100
- `top_trends`: 10
- `top_signals`: 10
- `top_opportunities`: 10

Conclusion:

The Trend reporting pipeline still reads correctly and can build report data from the current JSON source.

Important caveat:

This confirms compatibility, not SQLite cutover. The pipeline still reads `articles.json` through `core.utils.load_articles`.

### SQLite Database Validation

Read-only database inspection showed:

- Tables: `posts`, `schema_migrations`, `source_runs`, `sources`
- `posts` count: 1145
- `schema_migrations` count: 2
- `source_runs` count: 0
- `sources` count: 4
- Out-of-scope tables present: none

`posts` columns:

- `id`
- `source_id`
- `source_run_id`
- `source_type`
- `source_record_id`
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
- `created_at`
- `updated_at`
- `category`
- `analysis_json`
- `filter_data_json`

Foreign key note:

A direct `sqlite3` connection reported `PRAGMA foreign_keys = 0`. This is expected for raw SQLite connections unless foreign keys are enabled per connection. `SQLiteStorage` enables foreign keys when used. This reinforces that all database access must go through storage/repository boundaries.

## 1. Trend Pipeline Still Reads Correctly

Status: Pass for current behavior.

Evidence:

- `reporter.py:11` imports `load_articles`.
- `reporter.py:16` points to `articles.json`.
- `reporter.py:137` loads articles from JSON in `build_report_data`.
- Runtime validation produced expected report structures.

Architectural concern:

The pipeline still reads JSON, not SQLite repositories. This preserves behavior but does not satisfy the future target where SQLite is source of truth.

Recommendation:

Do not change this in Phase 3 retroactively. In the next cutover phase, add repository-backed read paths behind a compatibility boundary and compare outputs against the current JSON path before switching.

## 2. Direct JSON Reads Where Repositories Should Be Used

Status: Fail for final architecture, expected transitional debt for Phase 3.

Direct JSON reads remain in:

- `analyzer.py:20`, `analyzer.py:160`
- `reporter.py:16`, `reporter.py:137`
- `reports/weekly_brief.py:28`, `reports/weekly_brief.py:78`
- collectors under `core/collectors/*`
- `core/utils/utils.py:10-18`
- `database/migrate_articles_json.py:36-43`
- `stats/stats_manager.py:62-63`

Assessment:

Some JSON use is still valid:

- `database/migrate_articles_json.py` is an import utility.
- `JsonStorage` and JSON utility functions remain valid for import/export/backup/recovery.
- `stats/collection_stats.json` is outside the Phase 3 posts migration scope.

But active pipeline reads from `articles.json` should eventually move behind repositories:

- analyzer
- reporter
- weekly brief
- collectors, once source write paths are repository-backed

Risk:

SQLite is now populated, but active behavior still depends on JSON. This can cause divergence if new collections or analyses update `articles.json` without updating SQLite.

Recommendation:

Before any real cutover, add a clear dual-write or repository-backed write path. Do not let JSON and SQLite drift silently.

## 3. Direct SQL Outside Repositories

Status: Partial violation.

No raw SQL was found in modules, reports, or collectors.

Direct SQL exists outside repositories in:

- `core/storage/sqlite_storage.py`
- `database/migrate_articles_json.py:213-237`

Storage-layer SQL is acceptable because `SQLiteStorage` owns migrations and connection setup.

The migration utility SQL is more nuanced:

- Data writes use `SourceRepository` and `PostRepository`.
- Validation counts use direct `connection.execute(...)` calls in `database/migrate_articles_json.py:213-237`.

Assessment:

This violates a strict reading of "No direct SQL exists outside repositories." It does not violate data-write boundaries, but it does place validation query knowledge outside repositories.

Recommendation:

Move validation/count operations into repository methods or a dedicated read-only audit repository before the repository boundary is considered fully clean.

## 4. Database Schema vs DATABASE_PROPOSAL_V2

Status: Partial implementation only.

Implemented tables:

- `schema_migrations`
- `sources`
- `source_runs`
- `posts`

Not implemented from V2 proposal:

- `evidence`
- `entities`
- `post_entities`
- `topics`
- `post_topics`
- `trends`
- `trend_observations`
- `trend_evidence`
- `complaints`
- `complaint_signals`
- `complaint_evidence`
- `friction_candidates`
- `friction_candidate_complaints`
- `friction_candidate_evidence`
- `frictions`
- `friction_evidence`
- `friction_workarounds`
- `validation_events`
- `reports`

This is consistent with the user's Phase 3 scope, which explicitly forbids creating trends, complaints, frictions, evidence, and friction objects.

### Schema Mismatches Inside Implemented Scope

`posts` differs from V2:

- Added in implementation but not in V2 `posts` proposal:
  - `category`
  - `analysis_json`
  - `filter_data_json`

Reason:

These were added to preserve existing JSON article data.

Risk:

`analysis_json` and `filter_data_json` can contain legacy scores/opinions such as relevance scores, trend-related outputs, or model-generated analysis. If treated as canonical platform fields, they conflict with Evidence-First philosophy.

Recommendation:

Document these as legacy preservation fields only. Long-term, they should either remain historical import payloads or move into generated artifact/report tables, not evidence-first canonical intelligence tables.

## 5. Repository Boundaries

Status: Mostly intact for writes, incomplete for reads/validation.

Good:

- `database/migrate_articles_json.py:109-111` constructs `SourceRepository` and `PostRepository`.
- Imported records are created through repository methods.
- Modules, engines, reports, and collectors do not execute raw SQL.

Problems:

- Migration validation reads counts through raw SQL in `database/migrate_articles_json.py:213-237`.
- Active application reads still use JSON utility functions rather than `PostRepository`.
- Repositories still call `storage.initialize()` in constructors, as noted in `PHASE2_AUDIT.md`.

Recommendation:

Add repository methods for:

- `PostRepository.count_posts`
- `PostRepository.count_distinct_urls`
- `PostRepository.count_with_raw_json`
- `PostRepository.list_by_date_range`
- `PostRepository.iter_all`

Then move migration validation and future reports to repository reads.

## Evidence-First Philosophy Review

### What Aligns

- Original JSON payload is preserved in `raw_json`.
- No trend, complaint, friction, or evidence objects were invented.
- No new scoring algorithms were added.
- SQLite posts preserve source, URL, title, content, metadata, analysis, and filter data for traceability.

### What Conflicts Or Needs Guardrails

1. `analysis_json` preserves model-generated analysis.

This is acceptable as imported historical data, but it is not evidence. Future code must avoid treating it as validated truth.

2. `filter_data_json` preserves relevance and matched-topic fields.

This is useful for migration completeness, but it may contain score-like fields. Under the evidence-first philosophy, these should be considered legacy generated metadata, not canonical evidence.

3. Active trend outputs still come from JSON pipeline scoring.

This preserves current behavior, but SQLite's evidence-first data model is not yet driving the pipeline.

4. No first-class evidence table exists yet.

This is correct for Phase 3 scope, but the database is not yet an evidence-first operational system. It is currently a post archive with preserved raw payloads.

## Future Migration Risks

### 1. JSON/SQLite Drift

Because collectors and analyzer still write JSON, future runs may update `articles.json` without updating SQLite.

Mitigation:

Implement a deliberate sync/cutover strategy before using SQLite as operational source of truth.

### 2. Legacy Score Contamination

`raw_json`, `analysis_json`, and `filter_data_json` preserve fields such as:

- `relevance_score`
- `trend_score`
- `opportunity_score`
- model analysis importance scores

Mitigation:

Keep these fields marked as imported legacy artifacts. Do not query them as canonical evidence-first values.

### 3. Source Runs Are Empty

`source_runs` has zero rows after migration.

This is understandable because the migration imported historical articles, not collection runs. But future lineage will be stronger if migration creates a source run for the import event or records import provenance elsewhere.

Mitigation:

In a future migration metadata phase, record import events separately or create source runs representing the import operation.

### 4. Source Identity Is Coarse

The migration created four source rows, likely by `source_type`, not by feed/repository/source origin.

Risk:

Multiple RSS feeds or GitHub query targets collapse into one source identity.

Mitigation:

Future source normalization should use more granular `sources` records, such as feed URL, repository host, subreddit, HN endpoint, or arXiv target.

### 5. Database Proposal V2 Encoding Issue

`DATABASE_PROPOSAL_V2.md` displays box-drawing characters as mojibake in the current environment.

Risk:

Architecture docs may be harder to read in some tools.

Mitigation:

Prefer ASCII diagrams in future architecture docs unless UTF-8 rendering is verified.

## Final Audit Verdict

Phase 3 is successful as a JSON-to-SQLite post import.

It is not yet a full SQLite cutover.

Pass:

- Trend pipeline still reads and computes correctly.
- JSON count matches SQLite post count.
- URL uniqueness is preserved.
- Raw JSON is preserved.
- No out-of-scope intelligence tables were created.
- Repository writes are used for migration data import.

Needs remediation:

- Active pipeline still reads JSON instead of repositories.
- Migration validation uses direct SQL outside repositories.
- Implemented schema is only a scoped subset of `DATABASE_PROPOSAL_V2`.
- Legacy score/opinion fields are preserved in JSON columns and need governance.
- Source identity is too coarse for long-term evidence-first traceability.

