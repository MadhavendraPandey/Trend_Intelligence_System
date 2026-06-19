-- Phase 10 evidence grouping foundation.
-- This migration creates only evidence group storage and membership links.
-- It intentionally does not create frictions, complaints, candidates,
-- opportunities, scores, rankings, extraction logic, or grouping algorithms.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS evidence_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'open',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_evidence_groups_status
    ON evidence_groups (status);

CREATE INDEX IF NOT EXISTS idx_evidence_groups_created
    ON evidence_groups (created_at);

CREATE TABLE IF NOT EXISTS evidence_group_members (
    group_id INTEGER NOT NULL,
    evidence_id INTEGER NOT NULL,
    PRIMARY KEY (group_id, evidence_id),
    FOREIGN KEY (group_id) REFERENCES evidence_groups (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_evidence_group_members_evidence
    ON evidence_group_members (evidence_id);
