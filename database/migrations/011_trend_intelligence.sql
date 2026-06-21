-- Trend Intelligence Migration
-- Supports: Trend Profiles, Snapshots, and Relationships

-- 1. Trend Profiles: Durable identities for emerging signals
CREATE TABLE trend_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    summary TEXT,
    description TEXT,
    domain TEXT,
    theme TEXT,
    trend_score REAL DEFAULT 0.0,
    trend_level TEXT, -- 'DOMINANT', 'STRONG', 'EMERGING', 'WEAK'
    confidence TEXT, -- 'HIGH', 'MEDIUM', 'LOW'
    mentions INTEGER DEFAULT 0,
    source_count INTEGER DEFAULT 0,
    category_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT
);

CREATE INDEX idx_trend_profiles_domain ON trend_profiles (domain);
CREATE INDEX idx_trend_profiles_theme ON trend_profiles (theme);
CREATE INDEX idx_trend_profiles_score ON trend_profiles (trend_score);

-- 2. Trend Snapshots: Immutable historical states for evolution tracking
CREATE TABLE trend_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trend_profile_id INTEGER NOT NULL,
    snapshot_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    trend_score REAL DEFAULT 0.0,
    mentions INTEGER DEFAULT 0,
    source_count INTEGER DEFAULT 0,
    category_count INTEGER DEFAULT 0,
    trend_level TEXT,
    metadata_json TEXT,
    FOREIGN KEY (trend_profile_id) REFERENCES trend_profiles (id) ON DELETE CASCADE
);

CREATE INDEX idx_trend_snapshots_profile ON trend_snapshots (trend_profile_id);
CREATE INDEX idx_trend_snapshots_at ON trend_snapshots (snapshot_at);

-- 3. Trend Relationships: Mapping connections between trends
CREATE TABLE trend_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_trend_id INTEGER NOT NULL,
    to_trend_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL, -- 'related', 'overlapping', 'dependent'
    explanation TEXT,
    supporting_evidence_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_trend_id) REFERENCES trend_profiles (id) ON DELETE CASCADE,
    FOREIGN KEY (to_trend_id) REFERENCES trend_profiles (id) ON DELETE CASCADE,
    UNIQUE(from_trend_id, to_trend_id, relationship_type)
);

CREATE INDEX idx_trend_relationships_from ON trend_relationships (from_trend_id);
CREATE INDEX idx_trend_relationships_to ON trend_relationships (to_trend_id);

-- 4. Trend Evidence Links: Connecting trends to atomic observations
CREATE TABLE trend_evidence (
    trend_profile_id INTEGER NOT NULL,
    evidence_id INTEGER NOT NULL,
    PRIMARY KEY (trend_profile_id, evidence_id),
    FOREIGN KEY (trend_profile_id) REFERENCES trend_profiles (id) ON DELETE CASCADE,
    FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id) ON DELETE CASCADE
);
