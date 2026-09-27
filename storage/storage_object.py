"""Object data returned by storage."""

from storage.storage_object_metadata import StorageObjectMetadata


class StorageObject:
    """Document bytes and concrete metadata describing the stored file."""

    def __init__(self, content: bytes, metadata: StorageObjectMetadata) -> None:
        self.content = content
        self.metadata = metadata
