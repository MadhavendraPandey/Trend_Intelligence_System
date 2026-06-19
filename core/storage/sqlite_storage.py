"""SQLite storage backend for the Intelligence Platform.

Purpose:
    Provide the primary durable storage implementation for platform data.
    Phase 1 creates only foundational tables: sources, source_runs, posts,
    and schema_migrations.

Architecture notes:
    SQLite is the platform source of truth. This class owns SQLite connection
    setup, foreign-key enforcement, and migration application. Repositories
    should depend on this storage object; modules, engines, and reports should
    not execute raw SQL directly.

Future extension guidance:
    Add future schema changes as numbered files under database/migrations.
    Keep migration execution here so database replacement or connection policy
    changes remain isolated from intelligence modules.
"""

import sqlite3
from pathlib import Path

from core.storage.storage_interface import StorageInterface

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_FILE = PROJECT_ROOT / "database" / "intelligence_platform.sqlite"
DEFAULT_MIGRATIONS_DIR = PROJECT_ROOT / "database" / "migrations"


class SQLiteStorage(StorageInterface):
    """Primary SQLite storage implementation."""

    def __init__(self, db_file=DEFAULT_DB_FILE, migrations_dir=DEFAULT_MIGRATIONS_DIR):
        self.db_file = Path(db_file)
        self.migrations_dir = Path(migrations_dir)
        self._connection = None

    def connect(self):
        """Return a SQLite connection with foreign keys enabled."""
        if self._connection is None:
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(self.db_file)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")

        return self._connection

    def initialize(self):
        """Apply pending SQL migrations."""
        connection = self.connect()
        self._ensure_schema_migrations_table(connection)

        for migration_file in self._migration_files():
            version = migration_file.stem

            if self._is_migration_applied(connection, version):
                continue

            sql = migration_file.read_text(encoding="utf-8")

            with connection:
                connection.executescript(sql)
                connection.execute(
                    """
                    INSERT INTO schema_migrations (version, name)
                    VALUES (?, ?)
                    """,
                    (version, migration_file.name),
                )

        return connection

    def health_check(self):
        """Return True when SQLite can respond and foreign keys are enabled."""
        try:
            connection = self.connect()
            row = connection.execute("PRAGMA foreign_keys").fetchone()
            return bool(row and row[0] == 1)
        except sqlite3.Error:
            return False

    def close(self):
        """Close the active SQLite connection, if any."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _migration_files(self):
        if not self.migrations_dir.exists():
            return []

        return sorted(self.migrations_dir.glob("*.sql"))

    def _ensure_schema_migrations_table(self, connection):
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()

    def _is_migration_applied(self, connection, version):
        row = connection.execute(
            """
            SELECT 1
            FROM schema_migrations
            WHERE version = ?
            """,
            (version,),
        ).fetchone()

        return row is not None
