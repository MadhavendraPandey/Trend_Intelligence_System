# Friction Candidate Architecture

## Purpose

Phase 12 creates candidate friction generation from evidence groups.

The output is:

```text
Evidence Groups
  -> Candidate Frictions
```

Candidate frictions are hypotheses. They are not validated frictions,
opportunities, market analysis, startup recommendations, revenue estimates,
priorities, scores, or rankings.

## Database Tables

### `friction_candidates`

Stores generated candidate friction hypotheses.

Fields:

- `id`
- `title`
- `description`
- `status`
- `created_at`
- `updated_at`
- `metadata_json`

Allowed statuses:

- `generated`
- `reviewed`
- `accepted`
- `rejected`

### `friction_candidate_groups`

Stores traceability links from candidates back to supporting evidence groups.

Fields:

- `friction_candidate_id`
- `evidence_group_id`

## Repository

`FrictionCandidateRepository` owns all database access for candidates and
candidate/group links.

The repository does not validate frictions, rank candidates, score candidates,
prioritize candidates, estimate revenue, perform market analysis, or recommend
business actions.

## Service

`FrictionCandidateGenerationService`:

- reads evidence groups through `EvidenceGroupRepository`
- calls an `LLMProvider`
- validates strict JSON responses
- persists candidate frictions through `FrictionCandidateRepository`
- persists supporting evidence group links through `friction_candidate_groups`
- supports batch generation
- supports regeneration without deleting previous candidates

## LLM Output Contract

The LLM must return:

```json
{
  "candidates": [
    {
      "title": "Short candidate friction title",
      "description": "Neutral hypothesis explaining the repeated obstacle.",
      "supporting_evidence_group_ids": [1, 2]
    }
  ]
}
```

Malformed responses are rejected.

Validation rules:

- root must be a JSON object
- `candidates` must be a list
- each candidate must have a non-empty `title`
- each candidate must have a non-empty `description`
- each candidate must have non-empty integer `supporting_evidence_group_ids`
- supporting group ids must come from the evidence group batch supplied to the model

## Traceability

Every candidate must be explainable through `friction_candidate_groups`, which
points back to evidence groups. Evidence groups point back to evidence records.

## Generation Metadata

Each candidate stores:

- `model_name`
- `provider_name`
- `generation_version`
- `generation_method`
- `created_at`
- `generation_run_id`
- `regeneration`
- `supporting_evidence_group_ids`

## Boundary Rules

Allowed:

- read evidence groups through `EvidenceGroupRepository`
- call an `LLMProvider`
- validate candidate JSON
- create candidate friction hypotheses
- link candidates to evidence groups

Forbidden:

- validated frictions
- opportunity detection
- market analysis
- startup recommendations
- revenue estimation
- prioritization
- scoring
- ranking
