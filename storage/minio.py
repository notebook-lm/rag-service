from minio import Minio

from storage.config import (
    MINIO_BUCKET,
    MINIO_ROOT_PASSWORD,
    MINIO_ROOT_USER,
    minio_connection,
)


class MinioClient:
    """MinIO object storage client for the configured RAG document bucket."""

    def __init__(self) -> None:
        endpoint, secure = minio_connection()
        self.bucket = MINIO_BUCKET
        self.client = Minio(
            endpoint,
            access_key=MINIO_ROOT_USER,
            secret_key=MINIO_ROOT_PASSWORD,
            secure=secure,
        )

    def get_object(self, object_key: str):
        return self.client.get_object(self.bucket, object_key)
