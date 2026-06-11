RSS_COLLECTION_FREQUENCY = "every_6_hours"

RSS_FILTERS = {
    "duplicate_detection": True,
    "interest_relevance": True,
    "content_length": True,
}

RSS_SIGNALS = [
    "title",
    "url",
    "published_date",
    "author",
    "content",
]

FEEDS = {
    "cybersecurity": [
        "https://feeds.feedburner.com/TheHackersNews",
        "https://www.bleepingcomputer.com/feed/",
        "https://krebsonsecurity.com/feed/",
        "https://www.darkreading.com/rss.xml",
        "https://www.securityweek.com/feed/",
        "https://www.schneier.com/feed/atom/",
    ],
    "ai": [
        "https://huggingface.co/blog/feed.xml",
        "https://openai.com/news/rss.xml",
        "https://www.anthropic.com/news/rss",
        "https://deepmind.google/blog/rss.xml",
        "https://www.marktechpost.com/feed/",
    ],
    "business": [
        # "https://hbr.org/",
        "https://feeds.feedburner.com/StrategyBusiness-AllUpdates/",
        "https://dowjones.io",
        "https://cnet.com",
        "https://venturebeat.com",
        "https://bothsidesofthetable.com",
    ],
    "startups": [
        "https://techcrunch.com/category/startups/feed/",
        "https://www.ycombinator.com/blog/feed",
        # "https://a16z.com/feed/",
        "https://www.saastr.com/feed/",
    ],
    "technology": [
        "https://www.technologyreview.com/feed/",
        "https://www.wired.com/feed/rss",
        "https://www.theverge.com/rss/index.xml",
        "https://arstechnica.com/feed/",
    ],
}
