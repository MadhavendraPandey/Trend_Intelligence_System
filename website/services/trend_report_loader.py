"""Presentation-layer access to trend reports.

The website does not generate or store trend reports — it only reads the
artifacts that modules.trend.reports owns. All loading logic lives there.
"""

from modules.trend.reports.loader import (
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
