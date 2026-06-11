import json
from datetime import datetime, timezone
from storage.sqlite_storage import connect

def save_snapshot(snapshot_type, data):
    """
    Saves a snapshot of trends or signals to the database.
    """
    with connect() as conn:
        conn.execute(
            "INSERT INTO snapshots (snapshot_type, data_json) VALUES (?, ?)",
            (snapshot_type, json.dumps(data, ensure_ascii=False))
        )
        conn.commit()

def get_latest_snapshot(snapshot_type):
    """
    Retrieves the most recent snapshot of a given type.
    """
    with connect() as conn:
        cursor = conn.execute(
            "SELECT data_json, timestamp FROM snapshots WHERE snapshot_type = ? ORDER BY timestamp DESC LIMIT 1",
            (snapshot_type,)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row["data_json"]), row["timestamp"]
    return None, None

def get_previous_snapshot(snapshot_type, before_timestamp):
    """
    Retrieves the most recent snapshot before a specific timestamp.
    """
    with connect() as conn:
        cursor = conn.execute(
            "SELECT data_json, timestamp FROM snapshots WHERE snapshot_type = ? AND timestamp < ? ORDER BY timestamp DESC LIMIT 1",
            (snapshot_type, before_timestamp)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row["data_json"]), row["timestamp"]
    return None, None
