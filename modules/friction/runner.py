"""Executable orchestration for the friction pipeline.

Purpose:
    Run the existing evidence extraction, evidence grouping, and candidate
    generation services as a single orchestrated pipeline.

Architecture notes:
    This runner only coordinates existing repositories, providers, and service
    objects. It does not add intelligence logic, validated frictions,
    opportunity detection, reports, scoring, or ranking.

Pipeline:
    Posts -> LLM Evidence Extraction -> Evidence -> LLM Evidence Grouping ->
    Evidence Groups -> Candidate Frictions

Future extension guidance:
    Keep new behavior in services and repositories. The runner should remain a
    thin orchestration shell with CLI plumbing and run summaries.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from typing import List, Optional

from core.llm import OpenAICompatibleProvider, OpenRouterProvider, QwenProvider
from core.storage import SQLiteStorage
from database.repositories import (
    EvidenceGroupRepository,
    EvidenceRepository,
    FrictionCandidateRepository,
    FrictionProfileRepository,
    FrictionSnapshotRepository,
    FrictionRelationshipRepository,
    FrictionContradictionRepository,
    PostRepository,
    SourceRepository,
)
from modules.friction.services import (
    FrictionCandidateGenerationService,
    FrictionProfileService,
    FrictionValidationService,
    LLMEvidenceGroupingService,
    EvolutionService,
    RelationshipService,
    ContradictionService,
)
from modules.friction.extractors import LLMEvidenceExtractor


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_DB_FILE = os.path.join(PROJECT_ROOT, "database", "intelligence_platform.sqlite")
DEFAULT_MIGRATIONS_DIR = os.path.join(PROJECT_ROOT, "database", "migrations")


@dataclass
class RunSummary:
    """Summary of one friction pipeline run."""

    posts_seen: int = 0
    evidence_created: int = 0
    evidence_groups_created: int = 0
    candidates_created: int = 0
    candidates_validated: int = 0
    profiles_synced: int = 0
    maturity_updates: int = 0
    dry_run: bool = False
    provider_name: str = "qwen"
    model_name: str = ""
    limit: Optional[int] = None
    elapsed_seconds: float = 0.0
    messages: Optional[List[str]] = None

    def add_message(self, message):
        if self.messages is None:
            self.messages = []
        self.messages.append(message)


def print_separator():
    print("=" * 70)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Friction pipeline runner for the Intelligence Platform"
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit posts processed")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan the run without writing evidence, groups, or candidates",
    )
    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="Skip generating a friction report after the pipeline run",
    )
    parser.add_argument(
        "--provider",
        default="qwen",
        choices=["qwen", "openai-compatible", "openrouter"],
        help="LLM provider to use",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override the provider model name",
    )
    return parser.parse_args()


def build_provider(provider_name, model_name):
    provider_name = provider_name.casefold()

    if provider_name == "qwen":
        return QwenProvider(model_name=model_name or "qwen2.5:3b")

    if provider_name == "openai-compatible":
        return OpenAICompatibleProvider(
            model_name=model_name or "qwen2.5:3b",
            base_url=os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "http://localhost:11434/v1"),
            api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
        )

    if provider_name == "openrouter":
        return OpenRouterProvider(
            model_name=model_name or "qwen/qwen-2.5-7b-instruct",
            api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        )

    raise ValueError(f"Unsupported provider: {provider_name}")


def initialize_repositories():
    storage = SQLiteStorage(
        db_file=DEFAULT_DB_FILE,
        migrations_dir=DEFAULT_MIGRATIONS_DIR,
    )
    return {
        "storage": storage,
        "sources": SourceRepository(storage),
        "posts": PostRepository(storage),
        "evidence": EvidenceRepository(storage),
        "evidence_groups": EvidenceGroupRepository(storage),
        "candidates": FrictionCandidateRepository(storage),
        "profiles": FrictionProfileRepository(storage),
        "snapshots": FrictionSnapshotRepository(storage),
        "relationships": FrictionRelationshipRepository(storage),
        "contradictions": FrictionContradictionRepository(storage),
    }


def run_pipeline(args):
    repositories = initialize_repositories()
    storage = repositories["storage"]
    provider = build_provider(args.provider, args.model)
    extractor = LLMEvidenceExtractor(
        repositories["posts"],
        repositories["evidence"],
        llm_provider=provider,
    )
    grouping_service = LLMEvidenceGroupingService(
        repositories["evidence"],
        repositories["evidence_groups"],
        llm_provider=provider,
    )
    candidate_service = FrictionCandidateGenerationService(
        repositories["evidence_groups"],
        repositories["candidates"],
        llm_provider=provider,
    )
    validation_service = FrictionValidationService(
        repositories["candidates"]
    )
    profile_service = FrictionProfileService(
        repositories["candidates"],
        repositories["profiles"]
    )
    evolution_service = EvolutionService(
        repositories["profiles"],
        repositories["snapshots"]
    )
    relationship_service = RelationshipService(
        repositories["relationships"],
        repositories["profiles"]
    )
    contradiction_service = ContradictionService(
        repositories["contradictions"],
        repositories["profiles"],
        repositories["candidates"],
        repositories["evidence"]
    )

    summary = RunSummary(
        dry_run=bool(args.dry_run),
        provider_name=provider.provider_name,
        model_name=provider.model_name,
        limit=args.limit,
    )

    try:
        summary.posts_seen = min(args.limit, repositories["posts"].count_posts()) if args.limit is not None else repositories["posts"].count_posts()

        if args.dry_run:
            summary.add_message("Dry run: no records were written.")
            summary.evidence_created = 0
            summary.evidence_groups_created = 0
            summary.candidates_created = 0
            return summary

        evidence_created = extractor.extract_from_posts(limit=args.limit or 1000)
        summary.evidence_created = len(evidence_created)

        grouped = grouping_service.group_ungrouped_evidence(max_evidence=args.limit)
        summary.evidence_groups_created = len(grouped)

        candidates = candidate_service.generate_from_groups(
            group_ids=[group["id"] for group in grouped] if grouped else None,
            max_groups=args.limit,
        )
        summary.candidates_created = len(candidates)

        if candidates:
            validated = []
            for cand in candidates:
                validated.append(validation_service.validate_candidate(cand["id"]))
            summary.candidates_validated = len(validated)
        else:
            # Fallback: Validate all existing 'generated' candidates if none were newly created
            # this helps catch up if previous runs were partial
            validated = validation_service.validate_all_candidates(status="generated")
            summary.candidates_validated = len(validated)

        # Sync accepted candidates to profiles
        synced_profiles = profile_service.sync_accepted_candidates()
        summary.profiles_synced = len(synced_profiles)

        # Process maturity layer for all active profiles
        profiles = repositories["profiles"].list_profiles(status="active", limit=1000)
        for profile in profiles:
            pid = profile["id"]
            evolution_service.process_profile_evolution(pid)
            relationship_service.discover_relationships(pid)
            contradiction_service.sync_contradictions_for_profile(pid)
            summary.maturity_updates += 1

        return summary
    finally:
        storage.close()


def print_summary(summary):
    print()
    print_separator()
    print("Run Summary")
    print_separator()
    print(f"Dry Run: {summary.dry_run}")
    print(f"Provider: {summary.provider_name}")
    print(f"Model: {summary.model_name}")
    if summary.limit is not None:
        print(f"Limit: {summary.limit}")
    print(f"Posts Seen: {summary.posts_seen}")
    print(f"Evidence Created: {summary.evidence_created}")
    print(f"Evidence Groups Created: {summary.evidence_groups_created}")
    print(f"Candidate Frictions Created: {summary.candidates_created}")
    print(f"Candidate Frictions Validated: {summary.candidates_validated}")
    print(f"Friction Profiles Synced: {summary.profiles_synced}")
    print(f"Maturity Layer Updates: {summary.maturity_updates}")
    print(f"Execution Time: {summary.elapsed_seconds:.2f} seconds")
    for message in summary.messages or []:
        print(message)


def main():
    args = parse_args()
    start_time = time.perf_counter()

    print_separator()
    print("FRICTION PIPELINE RUNNER")
    print_separator()
    print(f"Mode: {'dry-run' if args.dry_run else 'run'}")

    try:
        summary = run_pipeline(args)
        summary.elapsed_seconds = time.perf_counter() - start_time
        print_summary(summary)

        if not args.dry_run and not args.skip_report:
            sys.path.insert(0, PROJECT_ROOT)
            from friction_reporter import generate_report

            generate_report()

        return 0
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    except Exception as error:
        print()
        print_separator()
        print(f"Run failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
