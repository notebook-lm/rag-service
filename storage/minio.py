from minio import Minio

from storage.minio_config import MinioConfig


class MinioClient:
    """MinIO object storage client for the configured RAG document bucket."""

    def __init__(self, config: MinioConfig) -> None:
        self.bucket = config.bucket
        self.client = Minio(
            config.endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.secure,
        )

    def get_object(self, object_key: str):
        return self.client.get_object(self.bucket, object_key)
