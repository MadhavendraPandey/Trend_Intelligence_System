import json
from pathlib import Path

REPORTS_DIR = Path("reports/friction")

def get_latest_report_path():
    if not REPORTS_DIR.exists():
        return None

    json_files = list(REPORTS_DIR.glob("*_friction_report.json"))
    if not json_files:
        # Check for canonical name
        canonical = REPORTS_DIR / "friction_report.json"
        return canonical if canonical.exists() else None

    json_files.sort(reverse=True)
    return json_files[0]

def load_latest_report():
    path = get_latest_report_path()
    if not path:
        return None

    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None
