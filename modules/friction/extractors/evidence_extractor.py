"""Evidence extraction infrastructure for the friction module.

Purpose:
    Provide repository-backed extraction from posts into neutral evidence
    records. This file implements deterministic post-to-evidence extraction
    only; it does not contain complaint logic, friction scoring, candidate
    generation, clustering, validation, reports, LLM prompts, or opportunity
    detection.

Architecture notes:
    Extraction infrastructure depends on repositories, not raw SQL. Posts are
    read through `PostRepository`; evidence is written through
    `EvidenceRepository`. Evidence format is persisted in `evidence_type`,
    while evidence meaning is preserved in `metadata_json`.

Future extension guidance:
    Future implementations may subclass `BaseEvidenceExtractor` for alternate
    extraction strategies. They should emit `EvidenceDraft` objects that
    describe observable facts only. Any complaint, candidate, trend, grouping,
    clustering, validation, or report workflow must live in later approved
    phases.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import re
from typing import Dict, Optional

from database.repositories.evidence_repository import EvidenceRepository
from database.repositories.post_repository import PostRepository

SUPPORTED_EVIDENCE_FORMATS = frozenset(
    {
        "quote",
        "link",
        "metric",
        "comment",
        "repository_metadata",
        "paper_metadata",
        "manual_note",
    }
)

SUPPORTED_EVIDENCE_TYPES = SUPPORTED_EVIDENCE_FORMATS

SUPPORTED_EVIDENCE_MEANINGS = frozenset(
    {
        "Problem",
        "Failure",
        "Workaround",
        "Request",
        "Question",
        "Adoption",
        "Migration",
        "Research",
        "Release",
        "Observation",
    }
)

MEANING_PATTERNS = {
    "Problem": (
        "problem",
        "issue",
        "pain",
        "hard to",
        "difficult",
        "confusing",
        "struggle",
        "blocked",
    ),
    "Failure": (
        "failed",
        "failure",
        "error",
        "broken",
        "crash",
        "bug",
        "doesn't work",
        "does not work",
        "cannot",
        "can't",
    ),
    "Workaround": (
        "workaround",
        "work around",
        "instead",
        "ended up",
        "custom script",
        "hack",
        "manual step",
    ),
    "Request": (
        "please add",
        "feature request",
        "would like",
        "wish",
        "need support",
        "request",
        "could you add",
    ),
    "Question": (
        "how do",
        "how can",
        "why does",
        "what is",
        "anyone know",
        "is there",
        "can i",
        "should i",
    ),
    "Adoption": (
        "adopted",
        "using",
        "started using",
        "we use",
        "rolled out",
        "deployed",
    ),
    "Migration": (
        "migrated",
        "migration",
        "moving from",
        "moved from",
        "switching from",
        "switched from",
        "upgrade from",
    ),
    "Research": (
        "paper",
        "research",
        "study",
        "experiment",
        "benchmark",
        "evaluation",
    ),
    "Release": (
        "released",
        "release",
        "launched",
        "announced",
        "version",
        "changelog",
    ),
}

EXTRACTOR_VERSION = "phase8.rule_based.v1"
MAX_OBSERVATION_LENGTH = 500


@dataclass(frozen=True)
class EvidenceDraft:
    """Neutral evidence payload produced before repository persistence."""

    evidence_meaning: str
    observation: str
    evidence_format: str = "quote"
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    captured_at: Optional[str] = None
    context: Optional[str] = None
    metadata_json: Optional[Dict] = None

    @property
    def evidence_type(self):
        """Backward-compatible alias for the persisted evidence format."""
        return self.evidence_format


class BaseEvidenceExtractor(ABC):
    """Base interface for repository-backed evidence extraction."""

    supported_evidence_types = SUPPORTED_EVIDENCE_TYPES
    supported_evidence_formats = SUPPORTED_EVIDENCE_FORMATS
    supported_evidence_meanings = SUPPORTED_EVIDENCE_MEANINGS

    def __init__(self, post_repository, evidence_repository):
        if not isinstance(post_repository, PostRepository):
            raise TypeError("BaseEvidenceExtractor requires PostRepository")

        if not isinstance(evidence_repository, EvidenceRepository):
            raise TypeError("BaseEvidenceExtractor requires EvidenceRepository")

        self.post_repository = post_repository
        self.evidence_repository = evidence_repository

    def extract_from_posts(self, limit=100, offset=0):
        """Read posts through PostRepository and persist extracted evidence."""
        created = []

        for post in self.post_repository.list_posts(limit=limit, offset=offset):
            created.extend(self.extract_and_store_for_post(post))

        return created

    def extract_batch(self, batch_size=100, max_posts=None, offset=0):
        """Process posts in batches while preserving one-post-at-a-time extraction."""
        created = []
        current_offset = offset
        processed_posts = 0

        while True:
            if max_posts is not None:
                remaining = max_posts - processed_posts
                if remaining <= 0:
                    break

                current_limit = min(batch_size, remaining)
            else:
                current_limit = batch_size

            posts = self.post_repository.list_posts(
                limit=current_limit,
                offset=current_offset,
            )

            if not posts:
                break

            for post in posts:
                created.extend(self.extract_and_store_for_post(post))
                processed_posts += 1

            current_offset += len(posts)

            if len(posts) < current_limit:
                break

        return created

    def extract_and_store_for_post(self, post):
        """Extract draft evidence from one post and write it through the repository."""
        created = []

        for draft in self.extract_from_post(post):
            self._validate_draft(draft)
            created.append(self._store_draft(post, draft))

        return created

    @abstractmethod
    def extract_from_post(self, post):
        """Return neutral EvidenceDraft objects for a post.

        Implementations must not create complaints, friction candidates,
        frictions, validation events, scores, or reports.
        """

    def _store_draft(self, post, draft):
        metadata = self._metadata_for_draft(post, draft)
        return self.evidence_repository.create_evidence(
            post_id=post["id"],
            evidence_type=draft.evidence_format,
            observation=draft.observation,
            source_url=draft.source_url or post.get("url") or post.get("canonical_url"),
            source_type=draft.source_type or post.get("source_type"),
            author=draft.author or post.get("author"),
            published_at=draft.published_at or post.get("published_at"),
            captured_at=draft.captured_at,
            context=draft.context,
            metadata_json=metadata,
        )

    def _validate_draft(self, draft):
        if not isinstance(draft, EvidenceDraft):
            raise TypeError("extract_from_post must return EvidenceDraft objects")

        if draft.evidence_format not in self.supported_evidence_formats:
            raise ValueError(f"Unsupported evidence format: {draft.evidence_format}")

        if draft.evidence_meaning not in self.supported_evidence_meanings:
            raise ValueError(f"Unsupported evidence meaning: {draft.evidence_meaning}")

        if not draft.observation:
            raise ValueError("EvidenceDraft.observation is required")

    def _metadata_for_draft(self, post, draft):
        metadata = dict(draft.metadata_json or {})
        metadata.setdefault("evidence_meaning", draft.evidence_meaning)
        metadata.setdefault("evidence_format", draft.evidence_format)
        metadata.setdefault("extractor_version", EXTRACTOR_VERSION)
        metadata.setdefault("source_post_id", post.get("id"))
        return metadata


class EvidenceExtractor(BaseEvidenceExtractor):
    """Rule-based post-to-evidence extractor.

    The extractor emits neutral evidence from observable post content. It does
    not infer complaints, frictions, opportunities, candidates, clusters,
    validation state, scores, or rankings.
    """

    def extract_from_post(self, post):
        """Return EvidenceDraft objects extracted from one post."""
        text = self._post_text(post)

        if not text:
            return []

        evidence_format = self._infer_format(post)
        drafts = []

        for observation, meaning, matched_terms in self._meaningful_observations(text):
            drafts.append(
                EvidenceDraft(
                    evidence_meaning=meaning,
                    evidence_format=evidence_format,
                    observation=observation,
                    context=self._context_for_post(post),
                    metadata_json={
                        "matched_terms": matched_terms,
                        "extraction_method": "deterministic_keyword_scan",
                    },
                )
            )

        if drafts:
            return drafts

        return [
            EvidenceDraft(
                evidence_meaning="Observation",
                evidence_format=evidence_format,
                observation=self._trim_observation(text),
                context=self._context_for_post(post),
                metadata_json={
                    "matched_terms": [],
                    "extraction_method": "fallback_observation",
                },
            )
        ]

    def _meaningful_observations(self, text):
        observations = []
        seen = set()

        for sentence in self._sentences(text):
            observation = self._trim_observation(sentence)

            for meaning, matched_terms in self._classify_sentence(sentence):
                fingerprint = (meaning, observation.casefold())

                if fingerprint in seen:
                    continue

                seen.add(fingerprint)
                observations.append((observation, meaning, matched_terms))

        return observations

    def _classify_sentence(self, sentence):
        normalized = sentence.casefold()
        classifications = []

        if sentence.strip().endswith("?"):
            classifications.append(("Question", []))

        for meaning, patterns in MEANING_PATTERNS.items():
            matched_terms = [pattern for pattern in patterns if pattern in normalized]

            if matched_terms:
                classifications.append((meaning, matched_terms))

        return classifications

    def _sentences(self, text):
        normalized = re.sub(r"\s+", " ", text).strip()

        if not normalized:
            return []

        parts = re.split(r"(?<=[.!?])\s+|\n+", normalized)
        return [part.strip() for part in parts if part.strip()]

    def _post_text(self, post):
        values = [
            post.get("title"),
            post.get("content"),
        ]

        metadata = self._load_json(post.get("metadata_json"))

        for key in ("description", "summary", "comment"):
            if metadata.get(key):
                values.append(str(metadata[key]))

        return "\n".join(value for value in values if value)

    def _infer_format(self, post):
        source_type = (post.get("source_type") or "").casefold()

        if source_type == "github":
            return "repository_metadata"

        if source_type == "arxiv":
            return "paper_metadata"

        if source_type in {"reddit", "hackernews"}:
            return "comment"

        return "quote"

    def _context_for_post(self, post):
        title = post.get("title")
        url = post.get("url") or post.get("canonical_url")

        if title and url:
            return f"{title} ({url})"

        return title or url

    def _trim_observation(self, observation):
        cleaned = re.sub(r"\s+", " ", observation).strip()

        if len(cleaned) <= MAX_OBSERVATION_LENGTH:
            return cleaned

        return cleaned[: MAX_OBSERVATION_LENGTH - 3].rstrip() + "..."

    def _load_json(self, value):
        if isinstance(value, dict):
            return value

        if not value:
            return {}

        try:
            parsed = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return {}

        if isinstance(parsed, dict):
            return parsed

        return {}
