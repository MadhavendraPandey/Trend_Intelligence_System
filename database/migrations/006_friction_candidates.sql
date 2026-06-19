-- Phase 12 candidate friction foundation.
-- This migration creates only candidate friction hypotheses from evidence groups.
-- It intentionally does not create validated frictions, opportunities, scores,
-- rankings, market analysis, recommendations, revenue estimates, or priorities.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS friction_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'generated' CHECK (
        status IN (
            'generated',
            'reviewed',
            'accepted',
            'rejected'
        )
    ),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_friction_candidates_status
    ON friction_candidates (status);

CREATE INDEX IF NOT EXISTS idx_friction_candidates_created
    ON friction_candidates (created_at);

CREATE TABLE IF NOT EXISTS friction_candidate_groups (
    friction_candidate_id INTEGER NOT NULL,
    evidence_group_id INTEGER NOT NULL,
    PRIMARY KEY (friction_candidate_id, evidence_group_id),
    FOREIGN KEY (friction_candidate_id) REFERENCES friction_candidates (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (evidence_group_id) REFERENCES evidence_groups (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_friction_candidate_groups_group
    ON friction_candidate_groups (evidence_group_id);
