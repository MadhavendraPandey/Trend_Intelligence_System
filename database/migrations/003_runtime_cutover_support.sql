-- Phase 5 runtime cutover support.
-- Adds operational analyzer failure storage only.
-- Does not create trend, evidence, complaint, friction, topic, or entity tables.

ALTER TABLE source_runs ADD COLUMN quality_removed INTEGER NOT NULL DEFAULT 0;
ALTER TABLE source_runs ADD COLUMN irrelevant_removed INTEGER NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS analysis_failures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT,
    title TEXT,
    source_type TEXT,
    error TEXT,
    failed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analysis_failures_identifier
    ON analysis_failures (identifier);

CREATE INDEX IF NOT EXISTS idx_analysis_failures_failed_at
    ON analysis_failures (failed_at);
