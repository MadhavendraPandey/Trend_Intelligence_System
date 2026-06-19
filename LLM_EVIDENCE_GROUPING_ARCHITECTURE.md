# LLM Evidence Grouping Architecture

## Purpose

Phase 11 adds LLM-powered theme discovery over existing evidence records.

The output remains:

```text
Evidence
  -> Theme Groups
```

The service does not create frictions, complaints, opportunities, scores,
rankings, recommendations, or market validation.

## Flow

```text
EvidenceRepository
  -> LLMEvidenceGroupingService
  -> LLMProvider
  -> strict JSON validation
  -> EvidenceGroupRepository.create_group
  -> EvidenceGroupRepository.add_member
```

## Inputs

The service reads evidence records from `EvidenceRepository`.

Primary mode:

- `group_ungrouped_evidence`
- reads evidence with no existing group membership

Regrouping mode:

- `regroup_evidence`
- reads selected or all evidence records
- creates new groups without deleting evidence or existing groups

## LLM Output Contract

The LLM must return valid JSON:

```json
{
  "groups": [
    {
      "title": "Short neutral theme title",
      "description": "Brief explanation of the shared evidence theme.",
      "supporting_evidence_ids": [1, 2]
    }
  ]
}
```

Malformed responses are rejected.

Validation rules:

- root must be a JSON object
- `groups` must be a list
- each group must have a non-empty `title`
- each group must have a non-empty `description`
- each group must have non-empty integer `supporting_evidence_ids`
- supporting ids must come from the evidence batch supplied to the model

## Traceability

Every persisted group is explainable through `evidence_group_members`.

Each group stores metadata:

- `model_name`
- `provider_name`
- `grouping_version`
- `created_at`
- `grouping_method`
- `grouping_run_id`
- `regrouping`
- `supporting_evidence_ids`

The source evidence records remain unchanged.

## Batch Grouping

`group_evidence_records` processes supplied evidence in batches.

`group_ungrouped_evidence` and `regroup_evidence` both use the same batch
pipeline.

## Retry Handling

Provider failures and malformed responses are retried up to `max_retries`.

After all attempts fail, the service raises `LLMGroupingValidationError`.

## Boundary Rules

Allowed:

- read evidence through `EvidenceRepository`
- call an `LLMProvider`
- validate theme-group JSON
- create evidence groups
- create evidence group memberships

Forbidden:

- raw SQL in the service
- friction creation
- complaint creation
- opportunity detection
- scoring
- ranking
- business recommendations
- market validation
