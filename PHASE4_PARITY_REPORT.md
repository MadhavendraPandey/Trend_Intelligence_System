# Phase 4 Parity Report

## Summary

SQLite-backed report inputs were compared against the existing JSON path.

- All compared counts match: True
- JSON path remains available as fallback.
- No trend, evidence, complaint, or friction tables were created.

## Counts

| Metric | JSON Path | SQLite Path | Match |
| --- | ---: | ---: | --- |
| Articles | 1145 | 1145 | True |
| Trends | 15 | 15 | True |
| Signals | 15 | 15 | True |
| Opportunities | 15 | 15 | True |
| Top Trends In Report | 10 | 10 | True |
| Top Signals In Report | 10 | 10 | True |
| Top Opportunities In Report | 10 | 10 | True |

## Read Path Notes

- JSON articles were loaded from `articles.json`.
- SQLite articles were loaded through `PostRepository.iter_all`.
- `reporter.py` now prefers SQLite when available and falls back to JSON if SQLite is unavailable or empty.
- SQLite rows are converted back into existing article dictionaries using preserved `raw_json`, with column fallbacks for migrated fields.

## Out Of Scope

Phase 4 did not modify analyzer or collectors.

Phase 4 did not create:

- trend tables
- evidence tables
- complaint tables
- friction tables
