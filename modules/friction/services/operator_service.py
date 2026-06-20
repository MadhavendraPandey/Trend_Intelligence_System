"""Internal Operator Service for system monitoring and quality control.

Purpose:
    Provide high-level operational intelligence and system health metrics.
    Detect data quality issues like orphans or broken chains.

Philosophy:
    Transparency for the operator. Fact-based operational metrics only.
"""

import os

class OperatorService:
    """Service for operational health and data quality."""

    def __init__(self, operator_repository, storage):
        self.repo = operator_repository
        self.storage = storage

    def get_system_overview(self):
        """Return a bird's eye view of the system state."""
        db_path = self.storage.db_file
        db_size_mb = os.path.getsize(db_path) / (1024 * 1024) if os.path.exists(db_path) else 0

        tables = self.repo.list_tables()
        counts = {}
        for table in tables:
            counts[table] = self.repo.connection.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]

        latest_run = self.repo.connection.execute(
            "SELECT * FROM source_runs ORDER BY started_at DESC LIMIT 1;"
        ).fetchone()

        return {
            "db_size_mb": round(db_size_mb, 2),
            "table_counts": counts,
            "latest_run": dict(latest_run) if latest_run else None,
            "total_tables": len(tables)
        }

    def detect_orphans(self):
        """Detect orphaned records across the intelligence chain."""
        orphans = []

        # Evidence without Post
        count = self.repo.connection.execute(
            "SELECT COUNT(*) FROM evidence WHERE post_id NOT IN (SELECT id FROM posts);"
        ).fetchone()[0]
        if count > 0:
            orphans.append({"entity": "Evidence", "issue": "No matching Post", "count": count})

        # Groups without members
        count = self.repo.connection.execute(
            "SELECT COUNT(*) FROM evidence_groups WHERE id NOT IN (SELECT group_id FROM evidence_group_members);"
        ).fetchone()[0]
        if count > 0:
            orphans.append({"entity": "Evidence Groups", "issue": "No members", "count": count})

        # Candidates without groups
        count = self.repo.connection.execute(
            "SELECT COUNT(*) FROM friction_candidates WHERE id NOT IN (SELECT friction_candidate_id FROM friction_candidate_groups);"
        ).fetchone()[0]
        if count > 0:
            orphans.append({"entity": "Friction Candidates", "issue": "No linked Groups", "count": count})

        # Profiles without evidence
        count = self.repo.connection.execute(
            "SELECT COUNT(*) FROM friction_profiles WHERE evidence_count = 0;"
        ).fetchone()[0]
        if count > 0:
            orphans.append({"entity": "Friction Profiles", "issue": "Zero evidence count", "count": count})

        return orphans

    def get_storage_stats(self):
        """Return detailed storage statistics."""
        tables = self.repo.list_tables()
        stats = []
        for table in tables:
            # Simple row count growth estimation could go here
            count = self.repo.connection.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
            stats.append({"table": table, "rows": count})

        return sorted(stats, key=lambda x: x["rows"], reverse=True)
