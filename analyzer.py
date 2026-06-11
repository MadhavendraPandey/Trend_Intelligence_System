# Imports

import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime, timezone
from pathlib import Path

from utils import (
    clean_json_response,
    load_articles,
    save_articles,
)

# Configuration
# Configuration

PROJECT_ROOT = Path(__file__).resolve().parent

json_file = PROJECT_ROOT / "articles.json"

failed_articles_file = PROJECT_ROOT / "failed_articles.json"
MAX_ANALYSIS_PER_RUN = 50
CHECKPOINT_EVERY = 10
MAX_RETRIES = 2
ANALYSIS_TIMEOUT_SECONDS = 45
FAST_ANALYSIS_MODE = True
FAST_CONTENT_LIMIT = 600
STANDARD_CONTENT_LIMIT = 1500
MINIMUM_RELEVANCE_SCORE = 25
FAST_MODE_REMOVED_FIELDS = [
    "overview",
    "key_points",
    "why_it_matters",
]


def load_failed_articles():
    return load_articles(failed_articles_file)


def save_failed_articles(failed_articles):
    save_articles(failed_articles, failed_articles_file)


def get_article_identifier(article):
    return (
        article.get("url") or article.get("link") or article.get("title") or "unknown"
    )


def record_failed_article(article, error, failed_articles):
    failed_articles.append(
        {
            "identifier": get_article_identifier(article),
            "title": article.get("title", "Untitled"),
            "source_type": article.get("source_type", "rss"),
            "error": str(error),
            "failed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    save_failed_articles(failed_articles)


def analyze_with_timeout(content):

    from models.qwen import analyze

    with ThreadPoolExecutor(max_workers=1) as executor:

        future = executor.submit(analyze, content)

        return future.result(timeout=ANALYSIS_TIMEOUT_SECONDS)


def get_content_limit():
    if FAST_ANALYSIS_MODE:
        return FAST_CONTENT_LIMIT

    return STANDARD_CONTENT_LIMIT


def get_relevance_score(article):
    filter_data = article.get("filter_data") or {}
    return filter_data.get("relevance_score", 0) or 0


def get_priority(article):
    relevance_score = get_relevance_score(article)
    source_quality = article.get("source_quality", 0) or 0

    return relevance_score + source_quality


def get_unanalyzed_articles(articles):

    unanalyzed_articles = [
        article for article in articles if article.get("analysis") is None
    ]
    return sorted(
        unanalyzed_articles,
        key=get_priority,
        reverse=True,
    )


def get_candidate_articles(articles):

    unanalyzed_articles = get_unanalyzed_articles(articles)

    candidate_articles = [
        article
        for article in unanalyzed_articles
        if get_priority(article) >= MINIMUM_RELEVANCE_SCORE
    ]

    skipped_count = len(unanalyzed_articles) - len(candidate_articles)
    return (candidate_articles, skipped_count)


def analyze_article(article):

    content = article.get("content", "")[: get_content_limit()]

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = analyze_with_timeout(content)

            response = clean_json_response(response)

            return json.loads(response)

        except TimeoutError:

            last_error = (
                f"Analysis timed out "
                f"after "
                f"{ANALYSIS_TIMEOUT_SECONDS}"
                f" seconds"
            )

            print(f"Attempt " f"{attempt} " f"failed: " f"{last_error}")

        except Exception as error:

            last_error = error

            print(f"Attempt " f"{attempt} " f"failed: " f"{error}")

    raise RuntimeError(last_error)


def save_checkpoint(articles, processed_count):
    save_articles(articles, json_file)
    print(f"Checkpoint saved ({processed_count})")


def run_analyzer():
    articles = load_articles(json_file)
    failed_articles = load_failed_articles()
    candidate_articles, skipped_count = get_candidate_articles(articles)

    print(f"Loaded {len(articles)} articles")
    print(f"FAST_ANALYSIS_MODE: {FAST_ANALYSIS_MODE}")
    print(f"Content limit: {get_content_limit()} chars")
    print(f"Minimum relevance score: {MINIMUM_RELEVANCE_SCORE}")
    print(f"Candidate articles: {len(candidate_articles)}")
    print(f"Articles skipped: {skipped_count}")

    processed_count = 0
    analysis_times = []

    try:
        for article in candidate_articles:
            if processed_count >= MAX_ANALYSIS_PER_RUN:
                break

            print(f"\nAnalyzing: {article.get('title', 'Untitled')}")
            print(f"Relevance score: {get_relevance_score(article)}")
            start_time = time.perf_counter()

            try:
                article["analysis"] = analyze_article(article)
                processed_count += 1
                analysis_time = time.perf_counter() - start_time
                analysis_times.append(analysis_time)
                print("Analysis saved")
                print(f"Analysis time: {analysis_time:.2f} seconds")
                print_progress(
                    processed_count,
                    skipped_count,
                    analysis_times,
                    len(candidate_articles),
                )

                if processed_count % CHECKPOINT_EVERY == 0:
                    save_checkpoint(articles, processed_count)

            except Exception as error:
                print(f"Analysis failed: {error}")
                record_failed_article(article, error, failed_articles)
                save_checkpoint(articles, processed_count)
                continue

    except KeyboardInterrupt:
        print("\nInterrupted by user. Saving progress...")
        save_checkpoint(articles, processed_count)
        save_failed_articles(failed_articles)
        print("Progress saved. Exiting.")
        return

    except Exception as error:
        print(f"\nAnalyzer crashed: {error}")
        save_checkpoint(articles, processed_count)
        save_failed_articles(failed_articles)
        raise

    save_checkpoint(articles, processed_count)

    print_final_summary(
        processed_count, skipped_count, analysis_times, len(candidate_articles)
    )


def get_average_analysis_time(analysis_times):
    if not analysis_times:
        return 0

    return sum(analysis_times) / len(analysis_times)


def get_estimated_remaining_time(processed_count, analysis_times, total_candidates):
    average_time = get_average_analysis_time(analysis_times)
    remaining_count = max(
        0, min(total_candidates, MAX_ANALYSIS_PER_RUN) - processed_count
    )

    return average_time * remaining_count


def print_progress(processed_count, skipped_count, analysis_times, total_candidates):
    average_time = get_average_analysis_time(analysis_times)
    estimated_remaining = get_estimated_remaining_time(
        processed_count, analysis_times, total_candidates
    )

    print(f"Articles processed: {processed_count}")
    print(f"Articles skipped: {skipped_count}")
    print(f"Average analysis time: {average_time:.2f} seconds")
    print(f"Estimated remaining time: {estimated_remaining:.2f} seconds")


def print_final_summary(
    processed_count, skipped_count, analysis_times, total_candidates
):
    print("\nFinished.")
    print_progress(processed_count, skipped_count, analysis_times, total_candidates)


if __name__ == "__main__":
    run_analyzer()
