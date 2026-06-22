# Friction Intelligence Flow Audit

## Pipeline Stages

1. **Source**: Collection origins (RSS, GitHub, HN, Arxiv).
   - Table: `sources`
   - Repository: `SourceRepository`
2. **Evidence**: Atomic observations extracted from posts via LLM.
   - Table: `evidence`
   - Repository: `EvidenceRepository`
   - Service: `LLMEvidenceExtractor`
3. **Groups**: Collections of similar evidence items.
   - Table: `evidence_groups`, `evidence_group_members`
   - Repository: `EvidenceGroupRepository`
   - Service: `LLMEvidenceGroupingService`
4. **Candidates**: Proposed frictions generated from evidence groups.
   - Table: `friction_candidates`
   - Repository: `FrictionCandidateRepository`
   - Service: `FrictionCandidateGenerationService`, `FrictionValidationService`
5. **Profiles**: Durable, validated friction objects synced from accepted candidates.
   - Table: `friction_profiles`
   - Repository: `FrictionProfileRepository`
   - Service: `FrictionProfileService`
6. **Reporting**: Artifact generation for consumption.
   - Script: `friction_reporter.py` (Generates JSON/Markdown)
   - Loader: `website/services/friction_report_loader.py`
7. **Website**: Presentation layer.
   - Route: `/friction/reports`, `/report/friction-{id}`
   - Template: `report_list.html`, `report_detail.html`

## Intelligence Layers

- **Evolution**: Historical snapshots of profile metrics.
  - Table: `friction_snapshots`
  - Repository: `FrictionSnapshotRepository`
  - Service: `EvolutionService`
- **Relationships**: Mappings between related or overlapping frictions.
  - Table: `friction_relationships`
  - Repository: `FrictionRelationshipRepository`
  - Service: `RelationshipService`
- **Contradictions**: Evidence that challenges the friction profile.
  - Table: `friction_profile_contradictions`
  - Repository: `FrictionContradictionRepository`
  - Service: `ContradictionService`
