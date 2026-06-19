# SQLite Cutover Report

## Summary

Phase 5 makes SQLite the authoritative runtime store for article-shaped records
and collection stats.

Existing Trend pipeline functions keep their public call shape, but active
reads and writes now route through SQLite repositories:

- `load_articles(...)` reads SQLite posts.
- `save_articles(...)` writes SQLite posts.
- analyzer failure history is stored in SQLite.
- collection stats are stored in SQLite `source_runs`.
- reporter and weekly brief read SQLite-backed articles.

No dual-write mode was added. `articles.json` is no longer written by active
runtime helpers.

## Files Modified

- `core/utils/utils.py`
- `core/utils/__init__.py`
- `stats/stats_manager.py`
- `reporter.py`
- `reports/weekly_brief.py`
- `database/repositories/post_repository.py`
- `database/repositories/source_run_repository.py`
- `database/repositories/analysis_failure_repository.py`
- `database/repositories/__init__.py`
- `database/compare_report_parity.py`
- `database/migrations/003_runtime_cutover_support.sql`
- generated report artifacts:
  - `reports/daily/2026-06-19_report.md`
  - `reports/daily/2026-06-19_report.json`
  - `reports/weekly_brief_output.md`

## Files Created

- `database/repositories/source_run_repository.py`
- `database/repositories/analysis_failure_repository.py`
- `database/migrations/003_runtime_cutover_support.sql`
- `SQLITE_CUTOVER_REPORT.md`

## JSON Dependencies Removed From Active Runtime

### Utility Functions

Removed active JSON file reads/writes from:

- `core.utils.load_articles`
- `core.utils.save_articles`

These now use:

- `PostRepository`
- `SourceRepository`
- `AnalysisFailureRepository`
- `SQLiteStorage`

### Reporter

Removed JSON fallback from `reporter.py`.

Reporter now loads article-shaped records through:

- `SQLiteStorage`
- `PostRepository.iter_all`

### Stats Manager

Removed active runtime dependency on:

- `stats/collection_stats.json`

Stats now use:

- `SourceRunRepository`
- `source_runs`

Existing JSON stats were imported once into SQLite as aggregate source runs.

### Weekly Brief

Weekly brief no longer imports missing trend helper functions. It now reuses
`reporter.build_report_data()`, which reads from SQLite.

## Repository Methods Added

### `PostRepository`

- `upsert_article`
- `articles`
- `to_article`
- internal article conversion helpers

Existing Phase 4 read methods retained:

- `count_posts`
- `iter_all`
- `get_by_date_range`
- `get_by_source`
- `count_distinct_urls`

### `SourceRunRepository`

- `increment_stat`
- `get_stats`
- `replace_aggregate_stats`

### `AnalysisFailureRepository`

- `create_failure`
- `replace_failures`
- `list_failures`
- `get_failure`

## Remaining JSON Usage

Remaining JSON usage is not active article runtime storage:

- `core.storage.JsonStorage`
  - explicit import/export/backup/recovery utility
- `core.utils.export_articles_to_json`
  - explicit JSON export utility
- `database/migrate_articles_json.py`
  - historical migration utility for importing old `articles.json`
- `reporter.py`
  - writes report JSON artifact files, not article source storage
- `reports/weekly_brief.py`
  - writes markdown report artifact
- collectors
  - still have legacy variable names such as `json_file`, but calls now route
    through SQLite-backed `load_articles` and `save_articles`
- analyzer
  - still has legacy variable names such as `json_file` and
    `failed_articles_file`, but calls now route through SQLite-backed helpers

## Validation Results

### Compile Check

Command:

```text
.venv\Scripts\python.exe -m compileall -q analyzer.py main.py main_collector.py reporter.py scheduler.py core database modules reports stats
```

Result: passed.

### SQLite Migration Check

Applied Phase 5 support migration.

Current tables:

- `analysis_failures`
- `posts`
- `schema_migrations`
- `source_runs`
- `sources`

No trend, evidence, complaint, friction, topic, or entity tables were created.

### SQLite Article Runtime Read

Validation:

- `load_articles("articles.json")`
- Result: 1145 articles from SQLite
- First record has URL: True
- First record has `filter_data`: True

### Collector-Style Runtime Write

Validation:

- `save_articles(load_articles("articles.json"), "articles.json")`
- Result: passed
- Records processed: 1145

This validates the existing collector save pattern through SQLite-backed
helpers without running live network collection.

### Analyzer Runtime Read/Write

Validation:

- Loaded analyzer articles through `analyzer.load_articles(analyzer.json_file)`
- Ran `analyzer.save_checkpoint(...)`
- Result: passed
- Records processed: 1145

Analyzer LLM execution was not run because it would call the configured local
LLM and mutate analysis records. The SQLite-backed analyzer read/checkpoint
path was validated.

### Report Pipeline

Validation:

- `reporter.build_report_data()`
- `reporter.py`
- `main.py report`

Results:

- Total articles: 1145
- Top trends in report: 10
- Top signals in report: 10
- Top opportunities in report: 10
- `main.py report`: success

### Weekly Brief

Validation:

- `reports/weekly_brief.py`

Result: passed.

Weekly brief now uses the SQLite-backed reporter data path.

### Scheduler

Validation:

- scheduler import passed
- scheduler control flow passed with `run_command` patched to avoid launching
  live subprocesses
- scheduled daily calls detected: 3

The full scheduler was not executed because it would launch live collection and
LLM analysis subprocesses. Report and weekly report subprocess targets were
validated separately.

## Validation Limitations

Live network collection was not executed because collectors call external
services and mutate the database.

Full analyzer execution was not executed because it calls the configured local
LLM and mutates analysis records.

The validated cutover surface confirms that the existing collector/analyzer
read-write facades use SQLite, and that report/weekly report paths run from
SQLite.

## Explicitly Not Implemented

Phase 5 did not implement:

- evidence tables
- complaints
- frictions
- topics
- entities
- trend tables
- friction candidates
