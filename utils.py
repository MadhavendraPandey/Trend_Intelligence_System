# import
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# Clean JSON Response


def clean_json_response(response):

    response = response.strip()

    if "```json" in response:
        response = response.replace("```json", "")

    if "```" in response:
        response = response.replace("```", "")

    start = response.find("{")
    end = response.rfind("}")

    if start != -1 and end != -1:
        response = response[start : end + 1]

    return response.strip()


# collectors data


def create_item(
    source_type,
    category,
    title,
    content,
    url,
    metadata=None,
    filter_data=None,
):
    return {
        "source_type": source_type,
        "category": category,
        "title": title,
        "content": content,
        "url": url,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "source_quality_score": None,
        "trend_score": None,
        "opportunity_score": None,
        "analysis": None,
        "filter_data": (filter_data or {}),
        "metadata": (metadata or {}),
    }
