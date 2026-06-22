import json
import os
import sys
from datetime import date
from pathlib import Path

from core.storage import SQLiteStorage
from database.repositories import (
    FrictionProfileRepository,
    EvidenceRepository,
    SourceRepository,
    FrictionSnapshotRepository,
    FrictionRelationshipRepository,
    FrictionContradictionRepository,
    EvidenceGroupRepository,
    FrictionCandidateRepository,
    PostRepository
)

PROJECT_ROOT = Path(__file__).resolve().parent
sqlite_file = PROJECT_ROOT / "database" / "intelligence_platform.sqlite"
reports_dir = PROJECT_ROOT / "modules" / "friction" / "reports"

def ensure_report_directories():
    reports_dir.mkdir(parents=True, exist_ok=True)

def build_friction_report_data():
    storage = SQLiteStorage(db_file=sqlite_file)

    try:
        profile_repo = FrictionProfileRepository(storage)
        evidence_repo = EvidenceRepository(storage)
        source_repo = SourceRepository(storage)
        snapshot_repo = FrictionSnapshotRepository(storage)
        rel_repo = FrictionRelationshipRepository(storage)
        group_repo = EvidenceGroupRepository(storage)
        candidate_repo = FrictionCandidateRepository(storage)
        post_repo = PostRepository(storage)
        contra_repo = FrictionContradictionRepository(storage)

        profiles = profile_repo.list_profiles(status="active", limit=1000)

        report_data = {
            "generated_at": date.today().isoformat(),
            "overview": {
                "total_frictions": len(profiles),
                "total_evidence": evidence_repo.count_evidence(),
                "total_sources": source_repo.count_sources(),
            },
            "top_frictions": []
        }

        for profile in profiles:
            pid = profile["id"]

            # Traceability: Profile -> Candidate -> Groups -> Members -> Evidence -> Post -> Source
            supporting_evidence = []
            seen_evidence = set()

            cand_id = profile.get("candidate_friction_id")
            if cand_id:
                links = candidate_repo.list_groups(cand_id)
                for link in links:
                    group_id = link["evidence_group_id"]
                    members = group_repo.list_members(group_id)
                    for member in members:
                        ev_id = member["evidence_id"]
                        if ev_id not in seen_evidence:
                            seen_evidence.add(ev_id)
                            ev = evidence_repo.get_evidence(ev_id)
                            if ev:
                                post = post_repo.get_post(ev["post_id"])
                                source = source_repo.get_source(post["source_id"]) if post else None
                                supporting_evidence.append({
                                    "evidence": ev,
                                    "source": source
                                })

            # Basic info
            friction_item = {
                "id": pid,
                "title": profile["title"],
                "description": profile.get("description", ""),
                "validation_summary": profile["validation_summary"],
                "evidence_count": profile["evidence_count"],
                "source_count": profile["source_count"],
                "recurrence_count": profile["recurrence_count"],
                "contradiction_count": profile["contradiction_count"],
                "updated_at": profile["updated_at"],
                "evolution": None,
                "relationships": [],
                "contradictions": [],
                "supporting_evidence": supporting_evidence
            }

            # Evolution (latest snapshot)
            snapshots = snapshot_repo.list_for_profile(pid, limit=1)
            if snapshots:
                friction_item["evolution"] = snapshots[0]["classification"]

            # Relationships
            rels = rel_repo.list_for_profile(pid)
            for rel in rels:
                other_id = rel["to_profile_id"] if rel["from_profile_id"] == pid else rel["from_profile_id"]
                other = profile_repo.get_profile(other_id)
                if other:
                    friction_item["relationships"].append({
                        "id": other_id,
                        "title": other["title"],
                        "type": rel["relationship_type"]
                    })

            # Contradictions
            contras = contra_repo.list_for_profile(pid)
            for contra in contras:
                friction_item["contradictions"].append({
                    "evidence_id": contra["evidence_id"],
                    "observation": contra["observation"],
                    "reasoning": contra["reasoning"],
                    "source_type": contra["source_type"]
                })

            report_data["top_frictions"].append(friction_item)

        return report_data
    finally:
        storage.close()

def build_markdown_report(data):
    lines = [
        "# FRICTION INTELLIGENCE REPORT",
        f"Generated: {data['generated_at']}",
        "",
        "## Overview",
        f"- Total Frictions: {data['overview']['total_frictions']}",
        f"- Total Evidence: {data['overview']['total_evidence']}",
        f"- Total Sources: {data['overview']['total_sources']}",
        "",
        "## Top Frictions",
        ""
    ]

    for f in data["top_frictions"]:
        lines.append(f"### {f['title']}")
        lines.append(f"**Validation Summary:** {f['validation_summary']}")
        lines.append(f"- Evidence Count: {f['evidence_count']}")
        lines.append(f"- Source Count: {f['source_count']}")
        lines.append(f"- Recurrence Count: {f['recurrence_count']}")
        lines.append(f"- Contradiction Count: {f['contradiction_count']}")
        if f['evolution']:
            lines.append(f"- Evolution: {f['evolution']}")
        lines.append("")

    return "\n".join(lines)

def generate_report():
    ensure_report_directories()
    data = build_friction_report_data()

    today = date.today().isoformat()
    json_path = reports_dir / f"{today}_friction_report.json"
    md_path = reports_dir / f"{today}_friction_report.md"

    with open(json_path, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    with open(md_path, "w") as f:
        f.write(build_markdown_report(data))

    canonical_json = reports_dir / "friction_report.json"
    canonical_md = reports_dir / "friction_report.md"

    with open(canonical_json, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    with open(canonical_md, "w") as f:
        f.write(build_markdown_report(data))

    print(f"Friction report generated at {json_path}")

if __name__ == "__main__":
    generate_report()
