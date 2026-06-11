import json
import sqlite3
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

DEFAULT_DB_FILE = PROJECT_ROOT / "trend_intelligence.db"
DEFAULT_JSON_FILE = PROJECT_ROOT / "articles.json"


def connect(db_file=DEFAULT_DB_FILE):
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_file=DEFAULT_DB_FILE):
    with connect(db_file) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT,
                category TEXT,
                title TEXT NOT NULL,
                url TEXT UNIQUE,
                content TEXT,
                metadata_json TEXT,
                filter_data_json TEXT,
                created_at TEXT,
                collected_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                analysis_json TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(article_id) REFERENCES articles(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                relevance_score INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(article_id) REFERENCES articles(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                signal_strength REAL DEFAULT 0,
                signal_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(article_id) REFERENCES articles(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                snapshot_type TEXT NOT NULL,
                data_json TEXT NOT NULL
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_topics_topic ON topics(topic)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_type_time ON snapshots(snapshot_type, timestamp)")

        connection.commit()


def get_article_url(article):
    return article.get("url") or article.get("link")


def get_article_created_at(article):
    metadata = article.get("metadata") or {}

    return (
        article.get("created_at")
        or article.get("date")
        or metadata.get("created_at")
        or metadata.get("published")
        or metadata.get("published_at")
        or metadata.get("updated_at")
    )


def upsert_article(article, connection):
    cursor = connection.cursor()
    url = get_article_url(article)

    cursor.execute(
        """
        INSERT INTO articles (
            source_type,
            category,
            title,
            url,
            content,
            metadata_json,
            filter_data_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            source_type = excluded.source_type,
            category = excluded.category,
            title = excluded.title,
            content = excluded.content,
            metadata_json = excluded.metadata_json,
            filter_data_json = excluded.filter_data_json,
            created_at = excluded.created_at
        """,
        (
            article.get("source_type") or ("rss" if article.get("source") else "unknown"),
            article.get("category"),
            article.get("title", "Untitled"),
            url,
            article.get("content", ""),
            json.dumps(article.get("metadata") or {}, ensure_ascii=False),
            json.dumps(article.get("filter_data") or {}, ensure_ascii=False),
            get_article_created_at(article),
        )
    )

    cursor.execute(
        "SELECT id FROM articles WHERE url = ?",
        (url,)
    )
    row = cursor.fetchone()

    return row["id"] if row else None


def save_article_analysis(article_id, analysis, connection):
    if not analysis:
        return

    connection.execute(
        """
        INSERT INTO analysis (article_id, analysis_json)
        VALUES (?, ?)
        """,
        (
            article_id,
            json.dumps(analysis, ensure_ascii=False),
        )
    )


def save_article_topics(article_id, filter_data, connection):
    matched_topics = filter_data.get("matched_topics") or []
    relevance_score = filter_data.get("relevance_score", 0) or 0

    for topic in matched_topics:
        connection.execute(
            """
            INSERT INTO topics (article_id, topic, relevance_score)
            VALUES (?, ?, ?)
            """,
            (
                article_id,
                topic,
                relevance_score,
            )
        )


def save_article_signal(article_id, signal_strength, signal_data, connection):
    connection.execute(
        """
        INSERT INTO signals (article_id, signal_strength, signal_json)
        VALUES (?, ?, ?)
        """,
        (
            article_id,
            signal_strength,
            json.dumps(signal_data or {}, ensure_ascii=False),
        )
    )


def load_json_articles(json_file=DEFAULT_JSON_FILE):
    if not json_file.exists():
        return []

    with open(json_file, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def migrate_json_to_sqlite(
    json_file=DEFAULT_JSON_FILE,
    db_file=DEFAULT_DB_FILE
):
    initialize_database(db_file)
    articles = load_json_articles(json_file)

    with connect(db_file) as connection:
        for article in articles:
            article_id = upsert_article(article, connection)

            if not article_id:
                continue

            save_article_analysis(
                article_id,
                article.get("analysis"),
                connection
            )
            save_article_topics(
                article_id,
                article.get("filter_data") or {},
                connection
            )

        connection.commit()

    return len(articles)


if __name__ == "__main__":
    migrated = migrate_json_to_sqlite()
    print(f"Migrated {migrated} articles to {DEFAULT_DB_FILE}")
