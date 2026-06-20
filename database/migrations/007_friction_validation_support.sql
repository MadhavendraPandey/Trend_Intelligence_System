-- Phase 1: Friction Validation Core
-- Add metric columns and validation summary to friction_candidates table.

ALTER TABLE friction_candidates ADD COLUMN evidence_count INTEGER DEFAULT 0;
ALTER TABLE friction_candidates ADD COLUMN source_count INTEGER DEFAULT 0;
ALTER TABLE friction_candidates ADD COLUMN group_count INTEGER DEFAULT 0;
ALTER TABLE friction_candidates ADD COLUMN post_count INTEGER DEFAULT 0;
ALTER TABLE friction_candidates ADD COLUMN recurrence_count INTEGER DEFAULT 0;
ALTER TABLE friction_candidates ADD COLUMN contradiction_count INTEGER DEFAULT 0;
ALTER TABLE friction_candidates ADD COLUMN validation_summary TEXT;
