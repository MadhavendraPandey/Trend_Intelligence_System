# Phase 9 LLM Evidence Extractor Implementation Report

## Scope

Implemented an LLM-backed evidence extractor alongside the existing rule-based
extractor.

Architecture:

```text
BaseEvidenceExtractor
+-- EvidenceExtractor
+-- LLMEvidenceExtractor
```

## Files Created

- `core/llm/__init__.py`
- `core/llm/providers.py`
- `modules/friction/extractors/llm_evidence_extractor.py`
- `LLM_EVIDENCE_EXTRACTION_ARCHITECTURE.md`
- `PHASE9_IMPLEMENTATION_REPORT.md`

## Files Modified

- `modules/friction/extractors/__init__.py`

## Provider Support

Added provider abstraction:

- `LLMProvider`
- `QwenProvider`
- `OpenAICompatibleProvider`
- `OpenRouterProvider`
- `provider_from_environment`

Provider priority:

1. Qwen/local Ollama
2. OpenAI-compatible endpoint
3. OpenRouter

## Extractor Summary

`LLMEvidenceExtractor`:

- reads posts through `PostRepository`
- calls an `LLMProvider`
- validates strict JSON responses
- converts valid items into `EvidenceDraft`
- writes through inherited `EvidenceRepository` flow
- retries malformed or failed responses

## Output Contract

The LLM must return:

```json
{
  "evidence": []
}
```

or an evidence list containing:

- `evidence_meaning`
- `evidence_format`
- `observation`
- optional `source_url`
- optional `context`

Malformed responses are rejected.

## Metadata

LLM evidence drafts include:

- `extractor_version`
- `model_name`
- `provider_name`
- `extraction_method`
- `prompt_version`

## Explicitly Not Implemented

- Complaint Intelligence
- Friction Intelligence
- candidate generation
- clustering
- validation logic
- reports
- opportunity detection
- scores
- rankings
- recommendations

## Validation Results

Passed.

Checks run:

- Compile check:
  - `.venv\Scripts\python.exe -m compileall core\llm modules\friction\extractors core database main.py scheduler.py`
  - Result: passed
- Repository integration:
  - Created a temporary SQLite database.
  - Created source and post records through repositories.
  - Ran `LLMEvidenceExtractor` with a fake `LLMProvider`.
  - Persisted LLM-generated evidence through `EvidenceRepository`.
  - Result: passed
- LLM response validation:
  - Valid JSON evidence payload was accepted.
  - Non-JSON response was rejected.
  - Non-object root was rejected.
  - Missing `evidence` list was rejected.
  - Unsupported evidence meaning was rejected.
  - Unsupported evidence format was rejected.
  - Empty observation was rejected.
  - Result: passed
- EvidenceDraft conversion:
  - Valid LLM records were converted into `EvidenceDraft` objects only.
  - Evidence meaning and format were preserved.
  - Source URL, source type, author, context, and published date were carried
    from post or LLM output.
  - Result: passed
- Retry handling:
  - A malformed first response followed by a valid response succeeded with
    retry enabled.
  - Result: passed
- Provider selection:
  - `qwen` selected `QwenProvider`.
  - `openai_compatible` selected `OpenAICompatibleProvider`.
  - `openrouter` selected `OpenRouterProvider`.
  - Result: passed
- Boundary scan:
  - No raw SQL was added to the LLM extractor.
  - No complaint intelligence, friction intelligence, candidate generation,
    clustering, validation logic, reports, opportunity detection, scores,
    rankings, or recommendations were added.
  - Result: passed

Notes:

- Validation used a temporary SQLite database and fake LLM provider.
- No live collection, model call, network call, complaint, friction, candidate,
  clustering, validation, opportunity, or report workflow was executed.
