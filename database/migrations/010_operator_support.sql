-- Operator Console Support Migration
-- Tracks internal query history and operational metadata

CREATE TABLE operator_query_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT NOT NULL,
    executed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INTEGER,
    row_count INTEGER,
    status TEXT NOT NULL CHECK (status IN ('success', 'error')),
    error_message TEXT
);

CREATE INDEX idx_operator_query_history_at ON operator_query_history (executed_at);
