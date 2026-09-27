from email.utils import parsedate_to_datetime

from minio import Minio

from storage.minio_config import MinioConfig
from storage.storage import Storage
from storage.storage_object import StorageObject
from storage.storage_object_metadata import StorageObjectMetadata


class MinioClient(Storage):
    """MinIO object storage client for the configured RAG document bucket."""

    def __init__(self, config: MinioConfig) -> None:
        self.bucket = config.bucket
        self.client = Minio(
            config.endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.secure,
        )

    def get(self, object_key: str) -> StorageObject:
        response = self.client.get_object(self.bucket, object_key)
        try:
            return StorageObject(
                content=response.read(),
                metadata=StorageObjectMetadata(
                    content_type=response.headers.get("Content-Type"),
                    filename=response.headers.get("x-amz-meta-original-filename"),
                    size_bytes=int(response.headers["Content-Length"])
                    if response.headers.get("Content-Length")
                    else None,
                    etag=response.headers.get("ETag"),
                    last_modified=parsedate_to_datetime(response.headers["Last-Modified"])
                    if response.headers.get("Last-Modified")
                    else None,
                ),
            )
        finally:
            response.close()
            response.release_conn()
