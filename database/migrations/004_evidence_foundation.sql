-- Phase 6 evidence foundation for the Intelligence Platform.
-- This migration creates only first-class evidence and human validation events.
-- It intentionally does not create trend, complaint, friction, topic, or entity tables.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    evidence_type TEXT NOT NULL,
    observation TEXT NOT NULL,
    source_url TEXT,
    source_type TEXT,
    author TEXT,
    published_at TEXT,
    captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    context TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_evidence_post
    ON evidence (post_id);

CREATE INDEX IF NOT EXISTS idx_evidence_type
    ON evidence (evidence_type);

CREATE INDEX IF NOT EXISTS idx_evidence_source_type_published
    ON evidence (source_type, published_at);

CREATE INDEX IF NOT EXISTS idx_evidence_source_url
    ON evidence (source_url);

CREATE INDEX IF NOT EXISTS idx_evidence_captured
    ON evidence (captured_at);

CREATE TABLE IF NOT EXISTS validation_events (
    validation_event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    evidence_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (
        action IN (
            'validated',
            'rejected',
            'merged',
            'reopened',
            'needs_review'
        )
    ),
    reason TEXT,
    actor TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_validation_events_evidence
    ON validation_events (evidence_id);

CREATE INDEX IF NOT EXISTS idx_validation_events_action
    ON validation_events (action);

CREATE INDEX IF NOT EXISTS idx_validation_events_created
    ON validation_events (created_at);
