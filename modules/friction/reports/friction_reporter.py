"""Reporter for Friction Intelligence.

Purpose:
    Generate evidence-backed Friction Reports in JSON and Markdown formats
    from the durable identities in the database.
"""

import json
from pathlib import Path
from datetime import date

from modules.friction.services.traceability_service import TraceabilityService

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIR = PROJECT_ROOT / "reports"


class FrictionReporter:
    """Service for generating Friction reports."""

    def __init__(self, repos):
        self.profile_repo = repos["profiles"]
        self.traceability = TraceabilityService(repos)

    def generate_reports(self):
        """Generate JSON and Markdown report artifacts."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        profiles = self.profile_repo.list_profiles(status="active", limit=100)
        report_data = {
            "generated_at": date.today().isoformat(),
            "frictions": []
        }

        for profile in profiles:
            # Build full traceability chain for the report
            chain = self.traceability.build_profile_chain(profile["candidate_friction_id"])

            report_data["frictions"].append({
                "id": profile["id"],
                "title": profile["title"],
                "summary": profile["validation_summary"] or profile["description"],
                "evidence_count": profile["evidence_count"],
                "source_count": profile["source_count"],
                "traceability": chain
            })

        # Save JSON
        json_path = REPORTS_DIR / "friction_report.json"
        json_path.write_text(json.dumps(report_data, indent=4, ensure_ascii=False), encoding="utf-8")

        # Save Markdown
        md_path = REPORTS_DIR / "friction_report.md"
        self._write_markdown(report_data, md_path)

        return json_path, md_path

    def _write_markdown(self, data, path):
        lines = [
            "# FRICTION INTELLIGENCE REPORT",
            f"Generated: {data['generated_at']}\n",
            "## Executive Summary",
            f"This report identifies {len(data['frictions'])} recurring frictions validated across sources.\n"
        ]

        for friction in data["frictions"]:
            lines.append(f"### {friction['title']}")
            lines.append(f"- **Summary**: {friction['summary']}")
            lines.append(f"- **Evidence Points**: {friction['evidence_count']}")
            lines.append(f"- **Unique Sources**: {friction['source_count']}\n")

            lines.append("#### Evidence Chain")
            for group_link in friction["traceability"]:
                group = group_link["group"]
                lines.append(f"**Group: {group['title']}**")
                for member in group_link["evidence_members"]:
                    obs = member["evidence"]["observation"]
                    src = member["source"]["name"] if member["source"] else "Unknown Source"
                    lines.append(f"- \"{obs}\" ({src})")
            lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")
