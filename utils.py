# import
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# load Articles


def load_articles(json_file):
    json_file = Path(json_file)

    if not json_file.exists():
        return []

    with open(json_file, "r", encoding="utf-8") as file:
        try:
            return json.load(file)

        except json.JSONDecodeError:
            return []


# Save Articles


def save_articles(articles, json_file):
    json_file = Path(json_file).resolve()
    temp_file = json_file.with_suffix(json_file.suffix + ".tmp")

    last_error = None

    for attempt in range(5):
        try:
            with open(temp_file, "w", encoding="utf-8") as file:

                json.dump(articles, file, indent=4, ensure_ascii=False)

            try:
                temp_file.replace(json_file)
            except PermissionError:
                with open(json_file, "w", encoding="utf-8") as file:

                    json.dump(articles, file, indent=4, ensure_ascii=False)

                try:
                    temp_file.unlink()
                except FileNotFoundError:
                    pass

            return

        except OSError as error:
            last_error = error
            time.sleep(0.5 * (attempt + 1))

    raise last_error


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
