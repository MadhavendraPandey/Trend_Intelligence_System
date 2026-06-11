import os
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv as dotenv_load
except ImportError:
    dotenv_load = None


PROJECT_USER_AGENT = "trend-intelligence-reddit-collector/1.0"


def log_reddit_error(message):
    print(f"Reddit authentication error: {message}")


def load_env_file():
    if dotenv_load:
        dotenv_load()
        return


PROJECT_ROOT = (Path(__file__)
    .resolve()
    .parent
    .parent
)

env_file = PROJECT_ROOT / ".env"
    if not os.path.exists(env_file):
        return

    with open(env_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def get_reddit_client():
    load_env_file()

    try:
        import praw
    except ImportError as error:
        log_reddit_error(f"PRAW is not installed: {error}")
        return None

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT") or PROJECT_USER_AGENT

    if not client_id or not client_secret:
        log_reddit_error(
            "missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET in .env"
        )
        return None

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        reddit.user.me()
        return reddit

    except Exception as error:
        log_reddit_error(error)
        return None


def get_created_at(created_utc):
    if not created_utc:
        return None

    return datetime.fromtimestamp(
        created_utc,
        timezone.utc
    ).isoformat()


def submission_to_post(submission, listing_type):
    permalink = getattr(submission, "permalink", "") or ""
    reddit_url = f"https://www.reddit.com{permalink}.json" if permalink else ""
    created_utc = getattr(submission, "created_utc", None)

    return {
        "data": {
            "id": getattr(submission, "id", ""),
            "title": getattr(submission, "title", "") or "",
            "selftext": getattr(submission, "selftext", "") or "",
            "score": getattr(submission, "score", 0) or 0,
            "num_comments": getattr(submission, "num_comments", 0) or 0,
            "subreddit": str(getattr(submission, "subreddit", "") or ""),
            "created_utc": created_utc,
            "created_at": get_created_at(created_utc),
            "url": getattr(submission, "url", "") or reddit_url,
            "reddit_url": reddit_url,
            "permalink": permalink,
            "link_flair_text": (
                getattr(submission, "link_flair_text", "") or ""
            ),
            "collection_listings": [listing_type],
            "submission": submission,
        }
    }


def fetch_subreddit_posts(reddit, subreddit_name, listing_type, limit):
    if reddit is None:
        return []

    try:
        subreddit = reddit.subreddit(subreddit_name)
        listing = getattr(subreddit, listing_type)

        return [
            submission_to_post(submission, listing_type)
            for submission in listing(limit=limit)
        ]

    except Exception as error:
        print(
            f"Reddit collection error for r/{subreddit_name} "
            f"{listing_type}: {error}"
        )
        return []


def fetch_top_comments(submission, limit=3):
    if submission is None:
        return []

    try:
        submission.comment_sort = "top"
        submission.comments.replace_more(limit=0)
        comments = []

        for comment in submission.comments[:limit]:
            body = getattr(comment, "body", "") or ""

            if not body:
                continue

            comments.append({
                "author": str(getattr(comment, "author", "") or ""),
                "score": getattr(comment, "score", 0) or 0,
                "body": body,
            })

        return comments

    except Exception as error:
        print(f"Reddit comment fetch error: {error}")
        return []
