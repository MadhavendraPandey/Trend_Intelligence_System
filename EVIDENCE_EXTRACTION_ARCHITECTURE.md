# Evidence Extraction Architecture

## Purpose

Phase 7 introduces evidence extraction infrastructure only.

The extractor layer provides a stable path:

```text
posts
  -> PostRepository
  -> BaseEvidenceExtractor
  -> EvidenceDraft
  -> EvidenceRepository
  -> evidence
```

This phase does not implement extraction prompts, business rules, complaint
intelligence, friction intelligence, candidate generation, clustering,
validation logic, or reports.

## Location

Evidence extraction infrastructure lives in:

- `modules/friction/extractors/evidence_extractor.py`

The package is under `modules/friction` because friction will eventually need
evidence extraction first, but the evidence records created are neutral
platform evidence and remain reusable by future modules.

## Interfaces

### `EvidenceDraft`

An in-memory payload representing evidence before persistence.

Fields:

- `evidence_type`
- `observation`
- `source_url`
- `source_type`
- `author`
- `published_at`
- `captured_at`
- `context`
- `metadata_json`

### `BaseEvidenceExtractor`

Base interface for future extraction implementations.

Responsibilities:

- read posts through `PostRepository`
- call `extract_from_post`
- validate `EvidenceDraft` shape and evidence type
- write evidence through `EvidenceRepository`

Non-responsibilities:

- raw SQL
- complaint extraction
- friction extraction
- candidate generation
- clustering
- validation events
- LLM prompts
- scoring
- reporting

### `EvidenceExtractor`

Default Phase 7 shell implementation.

It returns no evidence until concrete extraction rules are approved. This keeps
the interface importable and testable without silently inventing extraction
behavior.

## Supported Evidence Types

The supported evidence types are taken from the repository evidence-first
database documentation:

- `quote`
- `link`
- `metric`
- `comment`
- `repository_metadata`
- `paper_metadata`
- `manual_note`

Unsupported evidence types are rejected before persistence.

## Dependency Rules

Allowed dependencies:

- extractor -> `PostRepository`
- extractor -> `EvidenceRepository`
- extractor -> evidence data contracts

Forbidden dependencies:

- extractor -> raw SQLite connection
- extractor -> reports
- extractor -> validation workflow
- extractor -> complaint tables
- extractor -> friction tables
- extractor -> trend tables
- extractor -> LLM prompts

## Future Extension Guidance

Future concrete extractors should subclass `BaseEvidenceExtractor` and
implement `extract_from_post(post)`.

That method should return `EvidenceDraft` objects only. Any higher-level
interpretation must be implemented in later approved phases after evidence has
been stored and remains traceable to source posts.
