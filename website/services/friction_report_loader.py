"""Presentation-layer access to friction reports.

The website does not generate or store friction reports — it only reads the
artifacts that modules.friction.reports owns. All loading logic lives there.
"""

from modules.friction.reports.loader import (
    get_latest_report_path,
    get_report_by_date,
    list_all_reports,
    load_latest_report,
)

__all__ = [
    "get_latest_report_path",
    "get_report_by_date",
    "list_all_reports",
    "load_latest_report",
]
