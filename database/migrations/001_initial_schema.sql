-- Phase 1 SQLite foundation for the Intelligence Platform.
-- This migration intentionally creates only foundational tables:
-- schema_migrations, sources, source_runs, and posts.
-- Trends, complaints, frictions, and evidence are intentionally out of scope.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    name TEXT NOT NULL,
    base_url TEXT,
    owner_module TEXT NOT NULL DEFAULT 'shared',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_type, name)
);

CREATE INDEX IF NOT EXISTS idx_sources_owner_module
    ON sources (owner_module);

CREATE TABLE IF NOT EXISTS source_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    status TEXT NOT NULL DEFAULT 'started',
    items_seen INTEGER NOT NULL DEFAULT 0,
    items_stored INTEGER NOT NULL DEFAULT 0,
    duplicates_seen INTEGER NOT NULL DEFAULT 0,
    errors_seen INTEGER NOT NULL DEFAULT 0,
    run_notes TEXT,
    metadata_json TEXT,
    FOREIGN KEY (source_id) REFERENCES sources (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_source_runs_source_started
    ON source_runs (source_id, started_at);

CREATE INDEX IF NOT EXISTS idx_source_runs_status
    ON source_runs (status);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    source_run_id INTEGER,
    source_type TEXT NOT NULL,
    source_record_id TEXT,
    url TEXT,
    canonical_url TEXT,
    title TEXT NOT NULL,
    content TEXT,
    author TEXT,
    published_at TEXT,
    captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    content_hash TEXT,
    language TEXT,
    raw_json TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES sources (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (source_run_id) REFERENCES source_runs (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_posts_canonical_url_unique
    ON posts (canonical_url)
    WHERE canonical_url IS NOT NULL AND canonical_url != '';

CREATE UNIQUE INDEX IF NOT EXISTS idx_posts_content_hash_unique
    ON posts (content_hash)
    WHERE content_hash IS NOT NULL AND content_hash != '';

CREATE INDEX IF NOT EXISTS idx_posts_source_type_published
    ON posts (source_type, published_at);

CREATE INDEX IF NOT EXISTS idx_posts_source_captured
    ON posts (source_id, captured_at);

CREATE INDEX IF NOT EXISTS idx_posts_source_record
    ON posts (source_type, source_record_id);
