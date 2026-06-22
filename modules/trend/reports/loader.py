"""Trend Intelligence report loading.

Purpose:
    Owns reading of generated trend report artifacts (JSON/Markdown) from
    this module's reports directory. Consumers (e.g. the website) should
    import from here rather than re-implementing report discovery logic.
"""

import json
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent / "daily"


def get_latest_report_path():
    """Find the latest JSON report with actual content."""
    if not REPORTS_DIR.exists():
        return None

    json_files = list(REPORTS_DIR.glob("*_report.json"))
    if not json_files:
        return None

    json_files.sort(reverse=True)

    for path in json_files:
        if path.stat().st_size > 2000:  # Heuristic for non-empty report
            return path

    return json_files[0]


def load_latest_report():
    """Load the most recent trend report."""
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
    path = REPORTS_DIR / f"{date_str}_report.json"
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def list_all_reports():
    """List all available trend reports."""
    if not REPORTS_DIR.exists():
        return []

    reports = []
    for path in sorted(REPORTS_DIR.glob("*_report.json"), reverse=True):
        reports.append({
            "date": path.stem.split("_")[0],
            "path": str(path),
        })
    return reports
