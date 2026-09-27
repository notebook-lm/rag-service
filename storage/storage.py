"""Abstract object storage contract."""

from abc import ABC, abstractmethod

from storage.storage_object import StorageObject


class Storage(ABC):
    """Load document objects from object storage."""

    @abstractmethod
    def get(self, object_key: str) -> StorageObject:
        """Return an object's content and storage metadata."""
