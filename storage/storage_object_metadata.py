"""File metadata returned by object storage."""

from datetime import datetime


class StorageObjectMetadata:
    """Describes a stored file without application event identifiers."""

    def __init__(
        self,
        content_type: str | None,
        filename: str | None,
        size_bytes: int | None,
        etag: str | None,
        last_modified: datetime | None,
    ) -> None:
        self.content_type = content_type
        self.filename = filename
        self.size_bytes = size_bytes
        self.etag = etag
        self.last_modified = last_modified
