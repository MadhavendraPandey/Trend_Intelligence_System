"""LLM-powered evidence theme grouping service.

Purpose:
    Discover theme groups from existing evidence records with an LLM provider
    and persist those groups through `EvidenceGroupRepository`.

Architecture notes:
    This service reads evidence through `EvidenceRepository`, persists groups
    and memberships through `EvidenceGroupRepository`, and calls a replaceable
    `LLMProvider` for theme discovery. It produces Evidence -> Theme Groups
    only. It does not create frictions, complaints, opportunities, rankings,
    scores, recommendations, market validation, or business conclusions.

Future extension guidance:
    Keep LLM grouping prompt and JSON validation strict. Future improvements
    may add prompt variants or batching policies, but higher-level intelligence
    objects must be introduced in separate approved phases.
"""

from datetime import datetime, timezone
import json
import time
from uuid import uuid4

from core.llm import LLMProvider, provider_from_environment
from database.repositories.evidence_group_repository import EvidenceGroupRepository
from database.repositories.evidence_repository import EvidenceRepository


GROUPING_VERSION = "phase11.llm_theme_grouping.v1"
GROUPING_METHOD = "llm_theme_discovery"

SYSTEM_PROMPT = """You group evidence records into neutral theme groups.

Rules:
- Return only valid JSON.
- Do not use markdown.
- Do not create frictions.
- Do not create complaints.
- Do not create opportunities.
- Do not create scores.
- Do not create rankings.
- Do not create recommendations.
- Create theme groups only.
- Every group must be explainable by its supporting evidence ids.
"""

USER_PROMPT_TEMPLATE = """Group the evidence records into neutral themes.

Return exactly this JSON shape:
{{
  "groups": [
    {{
      "title": "Short neutral theme title",
      "description": "Brief explanation of the shared evidence theme.",
      "supporting_evidence_ids": [1, 2]
    }}
  ]
}}

If there are no useful groups, return:
{{"groups": []}}

Only use evidence ids from the evidence_records list.
Do not invent evidence ids.
Do not rank groups.
Do not score groups.
Do not recommend actions.

Evidence records:
{evidence_records_json}
"""


class LLMGroupingValidationError(ValueError):
    """Raised when an LLM grouping response fails the JSON contract."""


class LLMEvidenceGroupingService:
    """LLM-powered service for Evidence -> Theme Groups."""

    def __init__(
        self,
        evidence_repository,
        evidence_group_repository,
        llm_provider=None,
        max_retries=2,
        retry_delay_seconds=0,
    ):
        if not isinstance(evidence_repository, EvidenceRepository):
            raise TypeError("LLMEvidenceGroupingService requires EvidenceRepository")

        if not isinstance(evidence_group_repository, EvidenceGroupRepository):
            raise TypeError(
                "LLMEvidenceGroupingService requires EvidenceGroupRepository"
            )

        if llm_provider is None:
            llm_provider = provider_from_environment()

        if not isinstance(llm_provider, LLMProvider):
            raise TypeError("LLMEvidenceGroupingService requires an LLMProvider")

        self.evidence_repository = evidence_repository
        self.evidence_group_repository = evidence_group_repository
        self.llm_provider = llm_provider
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    def group_ungrouped_evidence(self, batch_size=25, max_evidence=None):
        """Group evidence records that have no existing group membership."""
        evidence_records = self._list_ungrouped_evidence(max_evidence=max_evidence)
        return self.group_evidence_records(evidence_records, batch_size=batch_size)

    def regroup_evidence(self, evidence_ids=None, batch_size=25, max_evidence=None):
        """Create new theme groups without deleting evidence or existing groups."""
        evidence_records = self._list_evidence_for_regrouping(
            evidence_ids=evidence_ids,
            max_evidence=max_evidence,
        )
        return self.group_evidence_records(
            evidence_records,
            batch_size=batch_size,
            regrouping=True,
        )

    def group_evidence_records(self, evidence_records, batch_size=25, regrouping=False):
        """Group caller-supplied evidence records in batches."""
        created_groups = []
        records = list(evidence_records)

        for start in range(0, len(records), batch_size):
            batch = records[start : start + batch_size]

            if not batch:
                continue

            grouping_run_id = str(uuid4())
            payload = self._group_batch_with_retries(batch)
            created_groups.extend(
                self._persist_groups(
                    payload=payload,
                    batch=batch,
                    grouping_run_id=grouping_run_id,
                    regrouping=regrouping,
                )
            )

        return created_groups

    def build_prompt(self, evidence_records):
        """Build the theme discovery prompt for a batch of evidence records."""
        return USER_PROMPT_TEMPLATE.format(
            evidence_records_json=json.dumps(
                [self._prompt_record(record) for record in evidence_records],
                ensure_ascii=False,
                indent=2,
            )
        )

    def _group_batch_with_retries(self, evidence_records):
        prompt = self.build_prompt(evidence_records)
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
                    allowed_evidence_ids={
                        record["evidence_id"] for record in evidence_records
                    },
                )
            except Exception as exc:
                last_error = exc

                if attempt >= attempts - 1:
                    break

                if self.retry_delay_seconds:
                    time.sleep(self.retry_delay_seconds)

        raise LLMGroupingValidationError(
            f"LLM evidence grouping failed after {attempts} attempts"
        ) from last_error

    def _parse_response(self, response_text, allowed_evidence_ids):
        if not isinstance(response_text, str) or not response_text.strip():
            raise LLMGroupingValidationError("LLM response must be non-empty text")

        try:
            payload = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise LLMGroupingValidationError("LLM response is not valid JSON") from exc

        self._validate_payload(payload, allowed_evidence_ids)
        return payload

    def _validate_payload(self, payload, allowed_evidence_ids):
        if not isinstance(payload, dict):
            raise LLMGroupingValidationError("LLM response root must be an object")

        groups = payload.get("groups")

        if not isinstance(groups, list):
            raise LLMGroupingValidationError("LLM response must contain groups list")

        for group in groups:
            self._validate_group(group, allowed_evidence_ids)

    def _validate_group(self, group, allowed_evidence_ids):
        if not isinstance(group, dict):
            raise LLMGroupingValidationError("Group item must be an object")

        title = group.get("title")
        description = group.get("description")
        supporting_ids = group.get("supporting_evidence_ids")

        if not isinstance(title, str) or not title.strip():
            raise LLMGroupingValidationError("Group title is required")

        if not isinstance(description, str) or not description.strip():
            raise LLMGroupingValidationError("Group description is required")

        if not isinstance(supporting_ids, list) or not supporting_ids:
            raise LLMGroupingValidationError(
                "Group supporting_evidence_ids must be a non-empty list"
            )

        normalized_ids = set()

        for evidence_id in supporting_ids:
            if not isinstance(evidence_id, int) or isinstance(evidence_id, bool):
                raise LLMGroupingValidationError(
                    "Group supporting evidence ids must be integers"
                )

            if evidence_id not in allowed_evidence_ids:
                raise LLMGroupingValidationError(
                    f"Unsupported supporting evidence id: {evidence_id}"
                )

            normalized_ids.add(evidence_id)

        if not normalized_ids:
            raise LLMGroupingValidationError(
                "Group must contain at least one supporting evidence id"
            )

    def _persist_groups(self, payload, batch, grouping_run_id, regrouping=False):
        batch_by_id = {record["evidence_id"]: record for record in batch}
        created = []

        for group in payload["groups"]:
            supporting_ids = self._unique_ids(group["supporting_evidence_ids"])
            metadata = {
                "model_name": self.llm_provider.model_name,
                "provider_name": self.llm_provider.provider_name,
                "grouping_version": GROUPING_VERSION,
                "created_at": self._now(),
                "grouping_method": GROUPING_METHOD,
                "grouping_run_id": grouping_run_id,
                "regrouping": bool(regrouping),
                "supporting_evidence_ids": supporting_ids,
            }
            created_group = self.evidence_group_repository.create_group(
                title=group["title"].strip(),
                description=group["description"].strip(),
                status="theme",
                metadata_json=metadata,
            )

            for evidence_id in supporting_ids:
                if evidence_id not in batch_by_id:
                    raise LLMGroupingValidationError(
                        f"Cannot persist unsupported evidence id: {evidence_id}"
                    )

                self.evidence_group_repository.add_member(
                    group_id=created_group["id"],
                    evidence_id=evidence_id,
                )

            created.append(created_group)

        return created

    def _list_ungrouped_evidence(self, max_evidence=None):
        records = []
        offset = 0
        page_size = 250

        while True:
            page = self.evidence_repository.list_evidence(
                limit=page_size,
                offset=offset,
            )

            if not page:
                break

            for record in page:
                groups = self.evidence_group_repository.list_groups_for_evidence(
                    record["evidence_id"],
                    limit=1,
                )

                if groups:
                    continue

                records.append(record)

                if max_evidence is not None and len(records) >= max_evidence:
                    return records

            offset += len(page)

            if len(page) < page_size:
                break

        return records

    def _list_evidence_for_regrouping(self, evidence_ids=None, max_evidence=None):
        if evidence_ids is not None:
            records = []

            for evidence_id in evidence_ids:
                record = self.evidence_repository.get_evidence(evidence_id)

                if record is not None:
                    records.append(record)

                if max_evidence is not None and len(records) >= max_evidence:
                    break

            return records

        records = []
        offset = 0
        page_size = 250

        while True:
            page = self.evidence_repository.list_evidence(
                limit=page_size,
                offset=offset,
            )

            if not page:
                break

            records.extend(page)

            if max_evidence is not None and len(records) >= max_evidence:
                return records[:max_evidence]

            offset += len(page)

            if len(page) < page_size:
                break

        return records

    def _prompt_record(self, record):
        return {
            "evidence_id": record["evidence_id"],
            "evidence_type": record.get("evidence_type"),
            "observation": record.get("observation"),
            "source_url": record.get("source_url"),
            "source_type": record.get("source_type"),
            "author": record.get("author"),
            "published_at": record.get("published_at"),
            "context": record.get("context"),
            "metadata_json": record.get("metadata_json"),
        }

    def _unique_ids(self, evidence_ids):
        unique = []
        seen = set()

        for evidence_id in evidence_ids:
            if evidence_id in seen:
                continue

            unique.append(evidence_id)
            seen.add(evidence_id)

        return unique

    def _now(self):
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
