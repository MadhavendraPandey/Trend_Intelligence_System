"""Friction Intelligence report loading.

Purpose:
    Owns reading of generated friction report artifacts (JSON/Markdown) from
    this module's reports directory. Consumers (e.g. the website) should
    import from here rather than re-implementing report discovery logic.
"""

import json
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent


def get_latest_report_path():
    """Find the latest dated JSON friction report, falling back to the canonical file."""
    if not REPORTS_DIR.exists():
        return None

    json_files = list(REPORTS_DIR.glob("*_friction_report.json"))
    if not json_files:
        canonical = REPORTS_DIR / "friction_report.json"
        return canonical if canonical.exists() else None

    json_files.sort(reverse=True)
    return json_files[0]


def load_latest_report():
    """Load the most recent friction report."""
    path = get_latest_report_path()
    if not path:
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_report_by_date(date_str):
    """Load a report by date string (YYYY-MM-DD)."""
    path = REPORTS_DIR / f"{date_str}_friction_report.json"
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def list_all_reports():
    """List all available dated friction reports."""
    if not REPORTS_DIR.exists():
        return []

    reports = []
    for path in sorted(REPORTS_DIR.glob("*_friction_report.json"), reverse=True):
        reports.append({
            "date": path.stem.split("_")[0],
            "path": str(path),
        })
    return reports
