# Phase 8 Evidence Extraction Implementation Report

## Scope

Implemented the first working Post -> Evidence extraction system.

The extractor reads posts through `PostRepository`, processes posts one by one,
and writes evidence through `EvidenceRepository`.

Not implemented:

- Friction Intelligence
- Complaint Intelligence
- candidate generation
- clustering
- grouping
- opportunity detection
- validation logic
- reports
- LLM prompts

## Files Modified

- `modules/friction/extractors/evidence_extractor.py`

## Files Created

- `PHASE8_IMPLEMENTATION_REPORT.md`

## Extraction Flow

```text
PostRepository
  -> EvidenceExtractor.extract_from_posts
  -> EvidenceExtractor.extract_and_store_for_post
  -> EvidenceExtractor.extract_from_post
  -> EvidenceDraft
  -> EvidenceRepository.create_evidence
  -> evidence
```

## Evidence Meanings

Supported meanings:

- `Problem`
- `Failure`
- `Workaround`
- `Request`
- `Question`
- `Adoption`
- `Migration`
- `Research`
- `Release`
- `Observation`

Meanings are stored in `metadata_json` as `evidence_meaning`.

## Evidence Formats

Supported formats:

- `quote`
- `link`
- `metric`
- `comment`
- `repository_metadata`
- `paper_metadata`
- `manual_note`

Formats are stored in two places:

- `evidence.evidence_type` for compatibility with the Phase 6 schema.
- `metadata_json.evidence_format` to preserve explicit meaning/format separation.

## Extraction Method

The Phase 8 extractor uses deterministic keyword and punctuation cues.

It does not use:

- AI prompts
- model inference
- scoring
- confidence
- clustering
- grouping
- complaint generation
- friction generation

If no specific cue is found, the extractor creates a neutral `Observation`
evidence record from the post text.

## Batch Processing

Added `extract_batch`.

`extract_batch` reads posts in batches through `PostRepository` and still
processes each post independently through `extract_and_store_for_post`.

## Validation Results

Passed.

Checks run:

- Compile check:
  - `.venv\Scripts\python.exe -m compileall modules\friction\extractors core database main.py scheduler.py`
  - Result: passed
- Repository integration:
  - Created a temporary SQLite database.
  - Created sources through `SourceRepository`.
  - Created posts through `PostRepository`.
  - Ran `EvidenceExtractor` against repository-backed posts.
  - Wrote extracted evidence through `EvidenceRepository`.
  - Result: passed
- Evidence persistence:
  - Verified persisted evidence row count matched created evidence records.
  - Verified source references were present.
  - Verified `evidence.evidence_type` stored the evidence format.
  - Verified `metadata_json.evidence_meaning` stored the evidence meaning.
  - Verified `metadata_json.evidence_format` preserved the format separately.
  - Result: passed
- Sample extraction run:
  - Verified sample posts produced all supported meanings:
    - `Problem`
    - `Failure`
    - `Workaround`
    - `Request`
    - `Question`
    - `Adoption`
    - `Migration`
    - `Research`
    - `Release`
    - `Observation`
  - Result: passed
- Batch processing:
  - Verified `extract_batch` processes repository-backed posts in batches.
  - Verified each post is still processed through `extract_and_store_for_post`.
  - Result: passed
- Boundary scan:
  - No raw SQL was added to the extractor.
  - No complaint intelligence, friction intelligence, candidate generation,
    clustering, grouping, opportunity detection, validation logic, reports, LLM
    prompts, scores, or confidence fields were added.
  - Result: passed

Notes:

- Validation used a temporary SQLite database.
- No live collection, analysis, validation, trend, complaint, candidate,
  friction, clustering, grouping, opportunity, report, or LLM workflow was
  executed.
