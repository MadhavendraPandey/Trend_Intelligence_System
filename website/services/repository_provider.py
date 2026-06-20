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
    FrictionProfileRepository,
    PostRepository,
    SourceRepository,
    SourceRunRepository,
    OperatorRepository,
)


@contextmanager
def repository_scope(request):
    """Yield initialized repositories and close SQLite afterward."""
    repos = get_repositories(request)
    try:
        yield repos
    finally:
        repos["storage"].close()


def get_repositories(request):
    """Return initialized repositories for a request."""
    storage = SQLiteStorage(
        db_file=request.app.state.db_file,
        migrations_dir=request.app.state.migrations_dir,
    )
    storage.initialize()
    return {
        "storage": storage,
        "posts": PostRepository(storage),
        "evidence": EvidenceRepository(storage),
        "groups": EvidenceGroupRepository(storage),
        "candidates": FrictionCandidateRepository(storage),
        "profiles": FrictionProfileRepository(storage),
        "sources": SourceRepository(storage),
        "runs": SourceRunRepository(storage),
        "operator": OperatorRepository(storage),
    }

