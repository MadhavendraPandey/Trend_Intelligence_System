"""Repository for canonical post records.

Purpose:
    Own database access for normalized source observations stored in `posts`.
    Posts are the platform's base observation unit.

Architecture notes:
    This repository contains persistence operations only. It does not perform
    source collection, trend analysis, friction analysis, scoring, or JSON
    migration.

Future extension guidance:
    Add query methods around observed facts, source lineage, and date ranges.
    Keep module-specific intelligence queries in module repositories when
    those tables are introduced.
"""

import json

from core.storage import SQLiteStorage


class PostRepository:
    """CRUD repository for the `posts` table."""

    UPDATABLE_FIELDS = {
        "source_id",
        "source_run_id",
        "source_type",
        "source_record_id",
        "category",
        "url",
        "canonical_url",
        "title",
        "content",
        "author",
        "published_at",
        "captured_at",
        "content_hash",
        "language",
        "raw_json",
        "metadata_json",
        "analysis_json",
        "filter_data_json",
    }

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("PostRepository requires SQLiteStorage")

        self.storage = storage
        self.connection = storage.initialize()

    def create_post(
        self,
        source_id,
        source_type,
        title,
        source_run_id=None,
        source_record_id=None,
        category=None,
        url=None,
        canonical_url=None,
        content=None,
        author=None,
        published_at=None,
        captured_at=None,
        content_hash=None,
        language=None,
        raw_json=None,
        metadata_json=None,
        analysis_json=None,
        filter_data_json=None,
    ):
        """Create a post and return the inserted row."""
        raw_json = self._json_or_text(raw_json)
        metadata_json = self._json_or_text(metadata_json)
        analysis_json = self._json_or_text(analysis_json)
        filter_data_json = self._json_or_text(filter_data_json)

        cursor = self.connection.execute(
            """
            INSERT INTO posts (
                source_id,
                source_run_id,
                source_type,
                source_record_id,
                category,
                url,
                canonical_url,
                title,
                content,
                author,
                published_at,
                captured_at,
                content_hash,
                language,
                raw_json,
                metadata_json,
                analysis_json,
                filter_data_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP), ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                source_run_id,
                source_type,
                source_record_id,
                category,
                url,
                canonical_url,
                title,
                content,
                author,
                published_at,
                captured_at,
                content_hash,
                language,
                raw_json,
                metadata_json,
                analysis_json,
                filter_data_json,
            ),
        )
        self.connection.commit()
        return self.get_post(cursor.lastrowid)

    def upsert_article(self, article, source_id):
        """Insert or update a migrated article-shaped dictionary."""
        url = article.get("url") or article.get("link")
        existing = self.get_by_url(url) if url else None
        payload = self._article_to_post_fields(article, source_id)

        if existing:
            return self.update_post(existing["id"], **payload)

        return self.create_post(**payload)

    def get_post(self, post_id):
        """Return a post by id, or None when it does not exist."""
        row = self.connection.execute(
            """
            SELECT *
            FROM posts
            WHERE id = ?
            """,
            (post_id,),
        ).fetchone()
        return self._to_dict(row)

    def update_post(self, post_id, **fields):
        """Update allowed post fields and return the updated row."""
        updates = {
            key: self._json_or_text(value)
            for key, value in fields.items()
            if key in self.UPDATABLE_FIELDS
        }

        if not updates:
            return self.get_post(post_id)

        assignments = [f"{key} = ?" for key in updates]
        assignments.append("updated_at = CURRENT_TIMESTAMP")
        values = list(updates.values())
        values.append(post_id)

        self.connection.execute(
            f"""
            UPDATE posts
            SET {", ".join(assignments)}
            WHERE id = ?
            """,
            values,
        )
        self.connection.commit()
        return self.get_post(post_id)

    def get_by_url(self, url):
        """Return the first post matching url or canonical_url."""
        row = self.connection.execute(
            """
            SELECT *
            FROM posts
            WHERE url = ?
               OR canonical_url = ?
            ORDER BY id
            LIMIT 1
            """,
            (url, url),
        ).fetchone()
        return self._to_dict(row)

    def count_posts(self):
        """Return the total number of posts."""
        row = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM posts
            """
        ).fetchone()
        return row[0]

    def count_distinct_urls(self):
        """Return the count of distinct non-empty canonical URLs."""
        row = self.connection.execute(
            """
            SELECT COUNT(DISTINCT canonical_url)
            FROM posts
            WHERE canonical_url IS NOT NULL
              AND canonical_url != ''
            """
        ).fetchone()
        return row[0]

    def iter_all(self, batch_size=500):
        """Yield all posts in stable id order."""
        offset = 0

        while True:
            rows = self.connection.execute(
                """
                SELECT *
                FROM posts
                ORDER BY id
                LIMIT ?
                OFFSET ?
                """,
                (batch_size, offset),
            ).fetchall()

            if not rows:
                break

            for row in rows:
                yield self._to_dict(row)

            offset += batch_size

    def get_by_date_range(
        self,
        start_date=None,
        end_date=None,
        date_field="captured_at",
        limit=1000,
        offset=0,
    ):
        """Return posts within a date range using an approved date field."""
        allowed_date_fields = {
            "captured_at",
            "published_at",
            "created_at",
            "updated_at",
        }

        if date_field not in allowed_date_fields:
            raise ValueError(f"Unsupported date field: {date_field}")

        conditions = []
        values = []

        if start_date is not None:
            conditions.append(f"{date_field} >= ?")
            values.append(start_date)

        if end_date is not None:
            conditions.append(f"{date_field} <= ?")
            values.append(end_date)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        values.extend([limit, offset])
        rows = self.connection.execute(
            f"""
            SELECT *
            FROM posts
            {where_clause}
            ORDER BY {date_field}, id
            LIMIT ?
            OFFSET ?
            """,
            values,
        ).fetchall()

        return [self._to_dict(row) for row in rows]

    def get_by_source(self, source_type=None, source_id=None, limit=1000, offset=0):
        """Return posts by source type or source id."""
        return self.list_posts(
            source_id=source_id,
            source_type=source_type,
            limit=limit,
            offset=offset,
        )

    def articles(self):
        """Return all posts as existing article dictionaries."""
        return [self.to_article(post) for post in self.iter_all()]

    def list_posts(
        self,
        source_id=None,
        source_type=None,
        limit=100,
        offset=0,
    ):
        """Return posts, optionally filtered by source id or source type."""
        conditions = []
        values = []

        if source_id is not None:
            conditions.append("source_id = ?")
            values.append(source_id)

        if source_type is not None:
            conditions.append("source_type = ?")
            values.append(source_type)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        values.extend([limit, offset])
        rows = self.connection.execute(
            f"""
            SELECT *
            FROM posts
            {where_clause}
            ORDER BY captured_at DESC, id DESC
            LIMIT ?
            OFFSET ?
            """,
            values,
        ).fetchall()

        return [self._to_dict(row) for row in rows]

    def _json_or_text(self, value):
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)

        return value

    def _to_dict(self, row):
        if row is None:
            return None

        return dict(row)

    def _article_to_post_fields(self, article, source_id):
        metadata = article.get("metadata") or {}
        source_type = article.get("source_type") or article.get("source") or "unknown"
        return {
            "source_id": source_id,
            "source_type": source_type,
            "source_record_id": (
                article.get("id")
                or article.get("source_record_id")
                or metadata.get("story_id")
                or metadata.get("id")
                or metadata.get("full_name")
            ),
            "category": article.get("category"),
            "title": article.get("title") or "Untitled",
            "url": article.get("url") or article.get("link"),
            "canonical_url": article.get("url") or article.get("link"),
            "content": article.get("content"),
            "author": metadata.get("author"),
            "published_at": (
                article.get("published_at")
                or article.get("published")
                or article.get("date")
                or metadata.get("published_at")
                or metadata.get("published")
                or metadata.get("created_at")
                or metadata.get("updated_at")
            ),
            "captured_at": article.get("collected_at") or article.get("captured_at"),
            "raw_json": article,
            "metadata_json": metadata,
            "analysis_json": article.get("analysis"),
            "filter_data_json": article.get("filter_data") or {},
        }

    def to_article(self, post):
        """Convert a post row to the legacy article dictionary shape."""
        article = self._load_json_value(post.get("raw_json"), default={}) or {}

        if not isinstance(article, dict):
            article = {}

        article.setdefault("source_type", post.get("source_type"))
        article.setdefault("category", post.get("category"))
        article.setdefault("title", post.get("title"))
        article.setdefault("content", post.get("content") or "")
        article.setdefault("url", post.get("url") or post.get("canonical_url"))
        article.setdefault(
            "metadata",
            self._load_json_value(post.get("metadata_json"), default={}) or {},
        )
        article["analysis"] = self._load_json_value(post.get("analysis_json"))
        article["filter_data"] = (
            self._load_json_value(post.get("filter_data_json"), default={}) or {}
        )

        return article

    def _load_json_value(self, value, default=None):
        if value is None:
            return default

        if isinstance(value, (dict, list)):
            return value

        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return default
