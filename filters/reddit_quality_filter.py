MINIMUM_REDDIT_TEXT_LENGTH = 80
MINIMUM_ENGAGEMENT_SCORE = 5


def get_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def calculate_engagement_score(score, comments):
    return get_int(score) + (get_int(comments) * 2)


def engagement_score(post_data):
    return calculate_engagement_score(
        post_data.get("score", 0),
        post_data.get("num_comments", 0)
    )


def get_post_text(post_data):
    flair = post_data.get("link_flair_text") or ""

    return "\n".join([
        post_data.get("title", "") or "",
        post_data.get("selftext", "") or "",
        post_data.get("subreddit", "") or "",
        " ".join(flair.split()),
    ]).strip()


def is_high_quality_reddit_post(post_data):
    if not post_data:
        return False

    text = get_post_text(post_data)
    score = engagement_score(post_data)

    if len(text) >= MINIMUM_REDDIT_TEXT_LENGTH:
        return True

    return score >= MINIMUM_ENGAGEMENT_SCORE
