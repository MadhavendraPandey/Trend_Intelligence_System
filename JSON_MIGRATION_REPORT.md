# JSON Migration Report

## Summary

- JSON file: `articles.json`
- SQLite database: `database\intelligence_platform.sqlite`
- Total records: 1145
- Imported records: 1145
- Duplicate URLs: 0
- Skipped records: 0
- Failures: 0

## Validation Results

- SQLite post count: 1145
- Unique URL count: 1145
- Raw JSON rows: 1145
- Rows with category: 1145
- Rows with filter data: 1145
- Expected importable unique URLs: 1145
- Total accounted records equals JSON count: True
- SQLite count equals imported records: True
- URL uniqueness verified: True
- Raw JSON preserved for all imports: True

## Independent Validation

- JSON count: 1145
- SQLite `posts` count: 1145
- Distinct canonical URL count: 1145
- Rows with `raw_json`: 1145
- JSON URL set matches SQLite raw payload URL set: True
- Out-of-scope tables present: None
- Tables present: `posts`, `schema_migrations`, `source_runs`, `sources`
- Compile check: passed
- Smoke imports: passed

## Preservation Notes

The migration stores existing article fields in `posts`:

- `source_type`
- `category`
- `title`
- `content`
- `url`
- `metadata_json`
- `analysis_json`
- `filter_data_json`
- `raw_json`

The full original JSON object is preserved in `raw_json`.

## Out Of Scope

This migration did not create:

- trends
- complaints
- evidence
- frictions
- friction candidates

## Failures

- None
