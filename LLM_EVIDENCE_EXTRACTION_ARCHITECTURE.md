# LLM Evidence Extraction Architecture

## Purpose

Phase 9 adds an LLM-backed evidence extractor beside the existing rule-based
extractor.

```text
BaseEvidenceExtractor
+-- EvidenceExtractor
+-- LLMEvidenceExtractor
```

The LLM extractor performs only:

```text
Post
  -> LLM
  -> EvidenceDraft
  -> EvidenceRepository
```

It does not create complaints, frictions, candidates, clusters, validation
events, opportunities, scores, rankings, recommendations, or reports.

## Provider Architecture

LLM providers live in `core/llm`.

Supported provider priority:

1. `QwenProvider`
2. `OpenAICompatibleProvider`
3. `OpenRouterProvider`

All providers implement:

```text
LLMProvider.generate(prompt, system_prompt=None) -> str
```

Providers return raw model text only. Output validation belongs to
`LLMEvidenceExtractor`.

## Extractor Contract

`LLMEvidenceExtractor` subclasses `BaseEvidenceExtractor`.

It reads posts through `PostRepository` and persists evidence through
`EvidenceRepository`, inherited from the base extractor.

The LLM output must produce `EvidenceDraft` objects only.

## Prompt Objective

The prompt asks the model to extract atomic evidence records.

The prompt explicitly forbids:

- frictions
- opportunities
- scores
- rankings
- recommendations

The output must be valid JSON with an `evidence` list.

## Structured Output Contract

Required JSON shape:

```json
{
  "evidence": [
    {
      "evidence_meaning": "Problem",
      "evidence_format": "quote",
      "observation": "Exact atomic observation from the post.",
      "source_url": "https://source.example/item",
      "context": "Short source context"
    }
  ]
}
```

Valid evidence meanings:

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

Valid evidence formats:

- `quote`
- `link`
- `metric`
- `comment`
- `repository_metadata`
- `paper_metadata`
- `manual_note`

Malformed responses are rejected.

## Retry Handling

`LLMEvidenceExtractor` retries provider or validation failures up to
`max_retries`.

After all attempts fail, it raises `LLMResponseValidationError`.

## Metadata

Each LLM-generated `EvidenceDraft` includes:

- `extractor_version`
- `model_name`
- `provider_name`
- `extraction_method`
- `prompt_version`

The inherited repository persistence also stores:

- `evidence_meaning`
- `evidence_format`
- `source_post_id`

## Boundary Rules

The LLM extractor may:

- build prompts
- call an `LLMProvider`
- validate JSON
- create `EvidenceDraft` objects
- persist evidence through `EvidenceRepository`

The LLM extractor may not:

- execute raw SQL
- create complaints
- create frictions
- create candidates
- cluster or group evidence
- validate evidence
- create reports
- detect opportunities
- persist scores or rankings
