-- Phase 3 JSON migration support for existing Trend Intelligence articles.
-- This migration adds post-level preservation fields only.
-- It intentionally does not create trends, complaints, frictions, or evidence.

ALTER TABLE posts ADD COLUMN category TEXT;
ALTER TABLE posts ADD COLUMN analysis_json TEXT;
ALTER TABLE posts ADD COLUMN filter_data_json TEXT;

CREATE INDEX IF NOT EXISTS idx_posts_category
    ON posts (category);
