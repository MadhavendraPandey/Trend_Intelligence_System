"""Repository scope helpers for the Intelligence Workbench.

Purpose:
    Initialize SQLite storage and repositories for a single read-only request.

Architecture notes:
    Routes use this context manager instead of creating repositories directly.
    Database access remains owned by repository classes; the website only
    coordinates their read methods.

Future extension guidance:
    Add request caching or dependency injection here if the app grows, while
    keeping repository ownership unchanged.
"""

from __future__ import annotations

from contextlib import contextmanager

from core.storage import SQLiteStorage
from database.repositories import (
    EvidenceGroupRepository,
    EvidenceRepository,
    FrictionCandidateRepository,
    PostRepository,
    SourceRepository,
    SourceRunRepository,
)


@contextmanager
def repository_scope(request):
    """Yield initialized repositories and close SQLite afterward."""
    storage = SQLiteStorage(
        db_file=request.app.state.db_file,
        migrations_dir=request.app.state.migrations_dir,
    )
    storage.initialize()
    try:
        yield {
            "storage": storage,
            "posts": PostRepository(storage),
            "evidence": EvidenceRepository(storage),
            "groups": EvidenceGroupRepository(storage),
            "candidates": FrictionCandidateRepository(storage),
            "sources": SourceRepository(storage),
            "runs": SourceRunRepository(storage),
        }
    finally:
        storage.close()

