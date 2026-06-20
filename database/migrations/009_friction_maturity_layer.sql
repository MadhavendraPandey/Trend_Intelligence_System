-- Friction Maturity Layer Migration
-- Supports: Temporal Snapshots, Relationship Mapping, and Contradiction Intelligence

-- 1. Evolve friction_profiles with maturity fields
ALTER TABLE friction_profiles ADD COLUMN latest_classification TEXT;
ALTER TABLE friction_profiles ADD COLUMN latest_classification_reasoning TEXT;
ALTER TABLE friction_profiles ADD COLUMN contradiction_summary TEXT;
ALTER TABLE friction_profiles ADD COLUMN contradiction_ratio REAL DEFAULT 0.0;

-- 2. Create Snapshots table for immutable historical tracking
CREATE TABLE friction_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    snapshot_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    description TEXT,
    evidence_count INTEGER DEFAULT 0,
    source_count INTEGER DEFAULT 0,
    group_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    recurrence_count INTEGER DEFAULT 0,
    contradiction_count INTEGER DEFAULT 0,
    classification TEXT,
    classification_reasoning TEXT,
    metadata_json TEXT,
    FOREIGN KEY (profile_id) REFERENCES friction_profiles (id) ON DELETE CASCADE
);

CREATE INDEX idx_friction_snapshots_profile ON friction_snapshots (profile_id);
CREATE INDEX idx_friction_snapshots_at ON friction_snapshots (snapshot_at);

-- 3. Create Relationships table for friction-to-friction mapping
CREATE TABLE friction_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_profile_id INTEGER NOT NULL,
    to_profile_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL, -- 'related', 'overlapping', 'dependent', 'competing', 'causal_candidate'
    explanation TEXT,
    supporting_evidence_count INTEGER DEFAULT 0,
    supporting_source_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_profile_id) REFERENCES friction_profiles (id) ON DELETE CASCADE,
    FOREIGN KEY (to_profile_id) REFERENCES friction_profiles (id) ON DELETE CASCADE,
    UNIQUE(from_profile_id, to_profile_id, relationship_type)
);

CREATE INDEX idx_friction_relationships_from ON friction_relationships (from_profile_id);
CREATE INDEX idx_friction_relationships_to ON friction_relationships (to_profile_id);

-- 4. Create Contradiction Links for explicit surfacing of conflicting evidence
CREATE TABLE friction_profile_contradictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    evidence_id INTEGER NOT NULL,
    reasoning TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES friction_profiles (id) ON DELETE CASCADE,
    FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id) ON DELETE CASCADE,
    UNIQUE(profile_id, evidence_id)
);

CREATE INDEX idx_friction_profile_contradictions_profile ON friction_profile_contradictions (profile_id);
