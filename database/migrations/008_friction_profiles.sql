-- Phase 2: Friction Profiles
-- Add persistent Friction Profile layer.

CREATE TABLE friction_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_friction_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    validation_summary TEXT,
    evidence_count INTEGER DEFAULT 0,
    source_count INTEGER DEFAULT 0,
    group_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    recurrence_count INTEGER DEFAULT 0,
    contradiction_count INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active' CHECK (
        status IN ('active', 'archived')
    ),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT,
    FOREIGN KEY (candidate_friction_id) REFERENCES friction_candidates (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE INDEX idx_friction_profiles_status ON friction_profiles (status);
CREATE INDEX idx_friction_profiles_candidate ON friction_profiles (candidate_friction_id);
