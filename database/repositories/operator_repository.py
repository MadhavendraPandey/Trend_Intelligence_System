"""Repository for internal system operations.

Purpose:
    Provide meta-access to the database for the Operator Console.
    Handles table introspection, generic row retrieval, and restricted SQL.

Architecture notes:
    This repository is for internal use only. It supports dynamic queries
    required for the explorer and SQL studio.
"""

import time
from core.storage.sqlite_storage import SQLiteStorage


class OperatorRepository:
    """Internal repository for operator-level system access."""

    def __init__(self, storage):
        if not isinstance(storage, SQLiteStorage):
            raise TypeError("OperatorRepository requires SQLiteStorage")
        self.storage = storage
        self.connection = storage.initialize()

    def list_tables(self):
        """Return a list of all user tables in the database."""
        rows = self.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        ).fetchall()
        return [row["name"] for row in rows]

    def get_table_schema(self, table_name):
        """Return column information for a specific table."""
        # Validate table name to prevent injection in PRAGMA
        if table_name not in self.list_tables():
            raise ValueError(f"Invalid table name: {table_name}")

        rows = self.connection.execute(f"PRAGMA table_info({table_name});").fetchall()
        return [dict(row) for row in rows]

    def paginate_table(self, table_name, limit=50, offset=0, sort_col=None, sort_dir="DESC"):
        """Retrieve a page of rows from any table with generic sorting."""
        if table_name not in self.list_tables():
            raise ValueError(f"Invalid table name: {table_name}")

        # Basic validation for sort parameters
        columns = [c["name"] for c in self.get_table_schema(table_name)]
        if sort_col and sort_col not in columns:
             sort_col = None

        order_by = ""
        if sort_col:
            direction = "DESC" if sort_dir.upper() == "DESC" else "ASC"
            order_by = f"ORDER BY {sort_col} {direction}"

        rows = self.connection.execute(
            f"SELECT * FROM {table_name} {order_by} LIMIT ? OFFSET ?;",
            (limit, offset)
        ).fetchall()

        count = self.connection.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]

        return {
            "rows": [dict(row) for row in rows],
            "total_count": count,
            "columns": columns
        }

    def get_row(self, table_name, row_id, id_col="id"):
        """Retrieve a single row from any table."""
        if table_name not in self.list_tables():
            raise ValueError(f"Invalid table name: {table_name}")

        row = self.connection.execute(
            f"SELECT * FROM {table_name} WHERE {id_col} = ?;",
            (row_id,)
        ).fetchone()
        return dict(row) if row else None

    def execute_operator_sql(self, sql_text):
        """Execute a read-only SQL query and log history."""
        # Strict read-only check
        forbidden = {"INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE", "REPLACE"}
        first_word = sql_text.strip().split()[0].upper() if sql_text.strip() else ""

        if first_word in forbidden:
            raise PermissionError(f"Action {first_word} is not allowed in SQL Studio.")

        start_time = time.perf_counter()
        status = "success"
        error_msg = None
        rows = []

        try:
            cursor = self.connection.execute(sql_text)
            rows = cursor.fetchall()
            row_count = len(rows)
        except Exception as e:
            status = "error"
            error_msg = str(e)
            row_count = 0

        execution_time_ms = int((time.perf_counter() - start_time) * 1000)

        # Log query history
        self.connection.execute(
            """
            INSERT INTO operator_query_history (
                query_text, status, error_message, execution_time_ms, row_count
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (sql_text, status, error_msg, execution_time_ms, row_count)
        )
        self.connection.commit()

        if status == "error":
            raise Exception(error_msg)

        return {
            "rows": [dict(row) for row in rows],
            "columns": list(rows[0].keys()) if rows else [],
            "execution_time_ms": execution_time_ms,
            "row_count": row_count
        }

    def get_query_history(self, limit=50):
        """Return recent operator query history."""
        rows = self.connection.execute(
            "SELECT * FROM operator_query_history ORDER BY executed_at DESC LIMIT ?;",
            (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
