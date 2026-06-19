"""JSON import, export, and backup storage utilities.

Purpose:
    Preserve JSON compatibility for migration, backup, recovery, and tests.
    JSON is no longer the architectural source of truth once SQLite is
    initialized as the platform storage layer.

Architecture notes:
    This class intentionally performs file-level JSON operations only. It does
    not own intelligence behavior, scoring, reports, or SQLite migrations.

Future extension guidance:
    Keep JSON support focused on portability: import existing article files,
    export repository snapshots, and create timestamped backups before storage
    changes.
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from core.storage.storage_interface import StorageInterface


class JsonStorage(StorageInterface):
    """JSON compatibility storage for import/export/backup workflows."""

    def __init__(self, root_dir=None):
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()

    def initialize(self):
        """Ensure the JSON storage root exists."""
        self.root_dir.mkdir(parents=True, exist_ok=True)
        return self.root_dir

    def health_check(self):
        """Return True when the JSON root exists and is writable."""
        try:
            self.initialize()
            probe = self.root_dir / ".json_storage_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return True
        except OSError:
            return False

    def close(self):
        """JSON file operations do not hold persistent resources."""
        return None

    def load(self, json_file):
        """Load a JSON file, returning None when the file does not exist."""
        path = Path(json_file)

        if not path.exists():
            return None

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save(self, data, json_file):
        """Write JSON data atomically enough for backup/export workflows."""
        path = Path(json_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(path.suffix + ".tmp")

        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        temp_path.replace(path)
        return path

    def backup(self, json_file, backup_dir):
        """Create a timestamped copy of a JSON file."""
        source = Path(json_file)

        if not source.exists():
            raise FileNotFoundError(source)

        target_dir = Path(backup_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target = target_dir / f"{source.stem}.{timestamp}{source.suffix}"
        shutil.copy2(source, target)
        return target
