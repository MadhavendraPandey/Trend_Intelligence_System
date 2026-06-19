"""LLM-backed evidence extractor.

Purpose:
    Convert posts into neutral `EvidenceDraft` objects through a replaceable
    LLM provider, then persist them through the existing repository-backed
    extractor flow.

Architecture notes:
    This extractor sits beside the rule-based `EvidenceExtractor`. It reads
    posts through `PostRepository`, writes evidence through `EvidenceRepository`,
    and uses `core.llm` providers for model text generation. LLM output must be
    structured JSON and is rejected when malformed.

Future extension guidance:
    Add model-specific prompt variants only when needed. Keep output validation
    strict and keep higher-level workflows such as complaints, frictions,
    candidates, clustering, validation, opportunity detection, and reports out
    of this extractor.
"""

import json
import time

from core.llm import LLMProvider, provider_from_environment
from modules.friction.extractors.evidence_extractor import (
    BaseEvidenceExtractor,
    EvidenceDraft,
    SUPPORTED_EVIDENCE_FORMATS,
    SUPPORTED_EVIDENCE_MEANINGS,
)


LLM_EXTRACTOR_VERSION = "phase9.llm.v1"
PROMPT_VERSION = "phase9.evidence_extraction.v1"

SYSTEM_PROMPT = """You extract atomic evidence records.

Rules:
- Return only valid JSON.
- Do not use markdown.
- Do not generate frictions.
- Do not generate opportunities.
- Do not generate scores.
- Do not generate rankings.
- Do not generate recommendations.
- Extract evidence only.
"""

USER_PROMPT_TEMPLATE = """Extract atomic evidence records from this post.

Evidence meanings must be one of:
Problem, Failure, Workaround, Request, Question, Adoption, Migration, Research, Release, Observation

Evidence formats must be one of:
quote, link, metric, comment, repository_metadata, paper_metadata, manual_note

Return exactly this JSON shape:
{{
  "evidence": [
    {{
      "evidence_meaning": "Problem",
      "evidence_format": "quote",
      "observation": "Exact atomic observation from the post.",
      "source_url": "https://source.example/item",
      "context": "Short source context"
    }}
  ]
}}

If there is no evidence, return:
{{"evidence": []}}

Post metadata:
- id: {post_id}
- source_type: {source_type}
- source_url: {source_url}
- author: {author}
- published_at: {published_at}
- title: {title}

Post content:
{content}
"""


class LLMResponseValidationError(ValueError):
    """Raised when an LLM response does not match the evidence JSON contract."""


class LLMEvidenceExtractor(BaseEvidenceExtractor):
    """LLM-backed extractor that emits EvidenceDraft objects only."""

    def __init__(
        self,
        post_repository,
        evidence_repository,
        llm_provider=None,
        max_retries=2,
        retry_delay_seconds=0,
    ):
        super().__init__(post_repository, evidence_repository)

        if llm_provider is None:
            llm_provider = provider_from_environment()

        if not isinstance(llm_provider, LLMProvider):
            raise TypeError("LLMEvidenceExtractor requires an LLMProvider")

        self.llm_provider = llm_provider
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    def extract_from_post(self, post):
        """Return EvidenceDraft objects extracted from one post by an LLM."""
        prompt = self.build_prompt(post)
        response_text = self._generate_with_retries(prompt)
        payload = self._parse_response(response_text)
        return self._drafts_from_payload(payload, post)

    def build_prompt(self, post):
        """Build the evidence extraction prompt for one post."""
        return USER_PROMPT_TEMPLATE.format(
            post_id=post.get("id"),
            source_type=post.get("source_type") or "",
            source_url=post.get("url") or post.get("canonical_url") or "",
            author=post.get("author") or "",
            published_at=post.get("published_at") or "",
            title=post.get("title") or "",
            content=self._post_content(post),
        )

    def _generate_with_retries(self, prompt):
        attempts = self.max_retries + 1
        last_error = None

        for attempt in range(attempts):
            try:
                response_text = self.llm_provider.generate(
                    prompt=prompt,
                    system_prompt=SYSTEM_PROMPT,
                )
                self._parse_response(response_text)
                return response_text
            except Exception as exc:
                last_error = exc

                if attempt >= attempts - 1:
                    break

                if self.retry_delay_seconds:
                    time.sleep(self.retry_delay_seconds)

        raise LLMResponseValidationError(
            f"LLM evidence extraction failed after {attempts} attempts"
        ) from last_error

    def _parse_response(self, response_text):
        if not isinstance(response_text, str) or not response_text.strip():
            raise LLMResponseValidationError("LLM response must be non-empty text")

        try:
            payload = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise LLMResponseValidationError("LLM response is not valid JSON") from exc

        self._validate_payload(payload)
        return payload

    def _validate_payload(self, payload):
        if not isinstance(payload, dict):
            raise LLMResponseValidationError("LLM response root must be an object")

        evidence_items = payload.get("evidence")

        if not isinstance(evidence_items, list):
            raise LLMResponseValidationError("LLM response must contain evidence list")

        for item in evidence_items:
            self._validate_item(item)

    def _validate_item(self, item):
        if not isinstance(item, dict):
            raise LLMResponseValidationError("Evidence item must be an object")

        meaning = item.get("evidence_meaning")
        evidence_format = item.get("evidence_format")
        observation = item.get("observation")

        if meaning not in SUPPORTED_EVIDENCE_MEANINGS:
            raise LLMResponseValidationError(f"Unsupported evidence meaning: {meaning}")

        if evidence_format not in SUPPORTED_EVIDENCE_FORMATS:
            raise LLMResponseValidationError(
                f"Unsupported evidence format: {evidence_format}"
            )

        if not isinstance(observation, str) or not observation.strip():
            raise LLMResponseValidationError("Evidence observation is required")

    def _drafts_from_payload(self, payload, post):
        drafts = []

        for item in payload["evidence"]:
            drafts.append(
                EvidenceDraft(
                    evidence_meaning=item["evidence_meaning"],
                    evidence_format=item["evidence_format"],
                    observation=item["observation"].strip(),
                    source_url=item.get("source_url")
                    or post.get("url")
                    or post.get("canonical_url"),
                    source_type=post.get("source_type"),
                    author=post.get("author"),
                    published_at=post.get("published_at"),
                    context=item.get("context") or self._context_for_post(post),
                    metadata_json={
                        "extractor_version": LLM_EXTRACTOR_VERSION,
                        "model_name": self.llm_provider.model_name,
                        "provider_name": self.llm_provider.provider_name,
                        "extraction_method": "llm_structured_json",
                        "prompt_version": PROMPT_VERSION,
                    },
                )
            )

        return drafts

    def _post_content(self, post):
        values = [
            post.get("title"),
            post.get("content"),
        ]
        return "\n".join(value for value in values if value)

    def _context_for_post(self, post):
        title = post.get("title")
        url = post.get("url") or post.get("canonical_url")

        if title and url:
            return f"{title} ({url})"

        return title or url
