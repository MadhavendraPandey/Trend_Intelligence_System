"""LLM-powered friction candidate generation service.

Purpose:
    Generate candidate friction hypotheses from existing evidence groups and
    persist traceable links back to those groups.

Architecture notes:
    This service reads evidence groups through `EvidenceGroupRepository`, calls
    a replaceable `LLMProvider`, and persists candidates through
    `FrictionCandidateRepository`. It creates Candidate Frictions only. It does
    not create validated frictions, opportunities, market analysis, startup
    recommendations, revenue estimates, prioritization, scores, or rankings.

Future extension guidance:
    Keep candidate generation separate from validation. Future validation or
    opportunity workflows should consume candidates through repositories rather
    than adding decision logic here.
"""

from datetime import datetime, timezone
import json
import time
from uuid import uuid4

from core.llm import LLMProvider, provider_from_environment
from database.repositories.evidence_group_repository import EvidenceGroupRepository
from database.repositories.friction_candidate_repository import (
    FrictionCandidateRepository,
)


GENERATION_VERSION = "phase12.friction_candidate_generation.v1"
GENERATION_METHOD = "llm_candidate_generation_from_evidence_groups"

SYSTEM_PROMPT = """You generate candidate friction hypotheses from evidence groups.

Rules:
- Return only valid JSON.
- Do not use markdown.
- Do not create validated frictions.
- Do not create opportunities.
- Do not do market analysis.
- Do not make startup recommendations.
- Do not estimate revenue.
- Do not prioritize.
- Do not score.
- Do not rank.
- Generate candidate frictions only.
- Every candidate must reference its supporting evidence group ids.
"""

USER_PROMPT_TEMPLATE = """Generate candidate friction hypotheses from these evidence groups.

Return exactly this JSON shape:
{{
  "candidates": [
    {{
      "title": "Short candidate friction title",
      "description": "Neutral hypothesis explaining the repeated obstacle.",
      "supporting_evidence_group_ids": [1, 2]
    }}
  ]
}}

If there are no candidate frictions, return:
{{"candidates": []}}

Only use group ids from the evidence_groups list.
Do not invent group ids.
Do not rank candidates.
Do not score candidates.
Do not recommend business actions.
Do not validate the candidates.

Evidence groups:
{evidence_groups_json}
"""


class FrictionCandidateGenerationValidationError(ValueError):
    """Raised when an LLM candidate response fails the JSON contract."""


class FrictionCandidateGenerationService:
    """Generate candidate friction hypotheses from evidence groups."""

    def __init__(
        self,
        evidence_group_repository,
        friction_candidate_repository,
        llm_provider=None,
        max_retries=2,
        retry_delay_seconds=0,
    ):
        if not isinstance(evidence_group_repository, EvidenceGroupRepository):
            raise TypeError(
                "FrictionCandidateGenerationService requires EvidenceGroupRepository"
            )

        if not isinstance(friction_candidate_repository, FrictionCandidateRepository):
            raise TypeError(
                "FrictionCandidateGenerationService requires "
                "FrictionCandidateRepository"
            )

        if llm_provider is None:
            llm_provider = provider_from_environment()

        if not isinstance(llm_provider, LLMProvider):
            raise TypeError(
                "FrictionCandidateGenerationService requires an LLMProvider"
            )

        self.evidence_group_repository = evidence_group_repository
        self.friction_candidate_repository = friction_candidate_repository
        self.llm_provider = llm_provider
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    def generate_from_groups(self, group_ids=None, batch_size=25, max_groups=None):
        """Generate candidates from evidence groups."""
        groups = self._list_groups(group_ids=group_ids, max_groups=max_groups)
        return self.generate_from_group_records(groups, batch_size=batch_size)

    def regenerate_from_groups(self, group_ids=None, batch_size=25, max_groups=None):
        """Generate new candidates without deleting previous candidates."""
        groups = self._list_groups(group_ids=group_ids, max_groups=max_groups)
        return self.generate_from_group_records(
            groups,
            batch_size=batch_size,
            regeneration=True,
        )

    def generate_from_group_records(
        self,
        evidence_groups,
        batch_size=25,
        regeneration=False,
    ):
        """Generate candidates from caller-supplied evidence group records."""
        created_candidates = []
        groups = list(evidence_groups)

        for start in range(0, len(groups), batch_size):
            batch = groups[start : start + batch_size]

            if not batch:
                continue

            generation_run_id = str(uuid4())
            payload = self._generate_batch_with_retries(batch)
            created_candidates.extend(
                self._persist_candidates(
                    payload=payload,
                    batch=batch,
                    generation_run_id=generation_run_id,
                    regeneration=regeneration,
                )
            )

        return created_candidates

    def build_prompt(self, evidence_groups):
        """Build the candidate generation prompt for evidence groups."""
        return USER_PROMPT_TEMPLATE.format(
            evidence_groups_json=json.dumps(
                [self._prompt_group(group) for group in evidence_groups],
                ensure_ascii=False,
                indent=2,
            )
        )

    def _generate_batch_with_retries(self, evidence_groups):
        prompt = self.build_prompt(evidence_groups)
        attempts = self.max_retries + 1
        last_error = None

        for attempt in range(attempts):
            try:
                response_text = self.llm_provider.generate(
                    prompt=prompt,
                    system_prompt=SYSTEM_PROMPT,
                )
                return self._parse_response(
                    response_text=response_text,
                    allowed_group_ids={group["id"] for group in evidence_groups},
                )
            except Exception as exc:
                last_error = exc

                if attempt >= attempts - 1:
                    break

                if self.retry_delay_seconds:
                    time.sleep(self.retry_delay_seconds)

        raise FrictionCandidateGenerationValidationError(
            f"Friction candidate generation failed after {attempts} attempts"
        ) from last_error

    def _parse_response(self, response_text, allowed_group_ids):
        if not isinstance(response_text, str) or not response_text.strip():
            raise FrictionCandidateGenerationValidationError(
                "LLM response must be non-empty text"
            )

        try:
            payload = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise FrictionCandidateGenerationValidationError(
                "LLM response is not valid JSON"
            ) from exc

        self._validate_payload(payload, allowed_group_ids)
        return payload

    def _validate_payload(self, payload, allowed_group_ids):
        if not isinstance(payload, dict):
            raise FrictionCandidateGenerationValidationError(
                "LLM response root must be an object"
            )

        candidates = payload.get("candidates")

        if not isinstance(candidates, list):
            raise FrictionCandidateGenerationValidationError(
                "LLM response must contain candidates list"
            )

        for candidate in candidates:
            self._validate_candidate(candidate, allowed_group_ids)

    def _validate_candidate(self, candidate, allowed_group_ids):
        if not isinstance(candidate, dict):
            raise FrictionCandidateGenerationValidationError(
                "Candidate item must be an object"
            )

        title = candidate.get("title")
        description = candidate.get("description")
        supporting_ids = candidate.get("supporting_evidence_group_ids")

        if not isinstance(title, str) or not title.strip():
            raise FrictionCandidateGenerationValidationError(
                "Candidate title is required"
            )

        if not isinstance(description, str) or not description.strip():
            raise FrictionCandidateGenerationValidationError(
                "Candidate description is required"
            )

        if not isinstance(supporting_ids, list) or not supporting_ids:
            raise FrictionCandidateGenerationValidationError(
                "supporting_evidence_group_ids must be a non-empty list"
            )

        normalized_ids = set()

        for group_id in supporting_ids:
            if not isinstance(group_id, int) or isinstance(group_id, bool):
                raise FrictionCandidateGenerationValidationError(
                    "Supporting evidence group ids must be integers"
                )

            if group_id not in allowed_group_ids:
                raise FrictionCandidateGenerationValidationError(
                    f"Unsupported supporting evidence group id: {group_id}"
                )

            normalized_ids.add(group_id)

        if not normalized_ids:
            raise FrictionCandidateGenerationValidationError(
                "Candidate must contain at least one supporting evidence group id"
            )

    def _persist_candidates(
        self,
        payload,
        batch,
        generation_run_id,
        regeneration=False,
    ):
        batch_by_id = {group["id"]: group for group in batch}
        created = []

        for candidate in payload["candidates"]:
            supporting_ids = self._unique_ids(
                candidate["supporting_evidence_group_ids"]
            )
            metadata = {
                "model_name": self.llm_provider.model_name,
                "provider_name": self.llm_provider.provider_name,
                "generation_version": GENERATION_VERSION,
                "generation_method": GENERATION_METHOD,
                "created_at": self._now(),
                "generation_run_id": generation_run_id,
                "regeneration": bool(regeneration),
                "supporting_evidence_group_ids": supporting_ids,
            }
            created_candidate = self.friction_candidate_repository.create_candidate(
                title=candidate["title"].strip(),
                description=candidate["description"].strip(),
                status="generated",
                metadata_json=metadata,
            )

            for group_id in supporting_ids:
                if group_id not in batch_by_id:
                    raise FrictionCandidateGenerationValidationError(
                        f"Cannot persist unsupported evidence group id: {group_id}"
                    )

                self.friction_candidate_repository.add_group(
                    candidate_id=created_candidate["id"],
                    evidence_group_id=group_id,
                )

            created.append(created_candidate)

        return created

    def _list_groups(self, group_ids=None, max_groups=None):
        if group_ids is not None:
            groups = []

            for group_id in group_ids:
                group = self.evidence_group_repository.get_group(group_id)

                if group is not None:
                    groups.append(group)

                if max_groups is not None and len(groups) >= max_groups:
                    break

            return groups

        groups = []
        offset = 0
        page_size = 250

        while True:
            page = self.evidence_group_repository.list_groups(
                limit=page_size,
                offset=offset,
            )

            if not page:
                break

            groups.extend(page)

            if max_groups is not None and len(groups) >= max_groups:
                return groups[:max_groups]

            offset += len(page)

            if len(page) < page_size:
                break

        return groups

    def _prompt_group(self, group):
        return {
            "id": group["id"],
            "title": group.get("title"),
            "description": group.get("description"),
            "status": group.get("status"),
            "metadata_json": group.get("metadata_json"),
        }

    def _unique_ids(self, group_ids):
        unique = []
        seen = set()

        for group_id in group_ids:
            if group_id in seen:
                continue

            unique.append(group_id)
            seen.add(group_id)

        return unique

    def _now(self):
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
