"""Storage contracts for the Intelligence Platform.

Purpose:
    Define the boundary that modules and repositories depend on instead of
    depending directly on SQLite, JSON files, or any future database driver.

Architecture notes:
    Storage implementations own connection setup, initialization, and health
    checks. Repositories should use concrete storage objects to obtain
    connections or import/export data, while engines and reports should stay
    unaware of storage internals.

Future extension guidance:
    Keep this interface small. If the platform later adopts PostgreSQL or a
    remote service, add a new implementation behind this contract without
    changing intelligence modules.
"""

from abc import ABC, abstractmethod


class StorageInterface(ABC):
    """Base interface for platform storage backends."""

    @abstractmethod
    def initialize(self):
        """Prepare the storage backend for use."""

    @abstractmethod
    def health_check(self):
        """Return True when the storage backend can be reached."""

    @abstractmethod
    def close(self):
        """Release backend resources held by this storage object."""
