"""Service to load trend reports from JSON artifacts."""

import json
from pathlib import Path

REPORTS_DIR = Path("reports/daily")

def get_latest_report_path():
    """Find the latest JSON report in the reports directory with actual content."""
    if not REPORTS_DIR.exists():
        return None

    json_files = list(REPORTS_DIR.glob("*.json"))
    if not json_files:
        return None

    # Sort by filename descending
    json_files.sort(reverse=True)

    # Prefer files with content if latest is empty
    for path in json_files:
        if path.stat().st_size > 2000: # Heuristic for non-empty report
            return path

    return json_files[0]

def load_latest_report():
    """Load the most recent trend report."""
    path = get_latest_report_path()
    if not path:
        return None

    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None

def get_report_by_date(date_str):
    """Load a report by date string (YYYY-MM-DD)."""
    path = REPORTS_DIR / f"{date_str}_report.json"
    if not path.exists():
        return None

    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None

def list_all_reports():
    """List all available trend reports."""
    if not REPORTS_DIR.exists():
        return []

    reports = []
    for path in sorted(REPORTS_DIR.glob("*.json"), reverse=True):
        reports.append({
            "date": path.stem.split("_")[0],
            "path": str(path)
        })
    return reports
