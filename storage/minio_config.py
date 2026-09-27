"""MinIO client configuration."""

from urllib.parse import urlparse


class MinioConfig:
    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket: str,
    ) -> None:
        parsed_endpoint = urlparse(endpoint_url)
        if not parsed_endpoint.hostname:
            raise ValueError("MINIO_ENDPOINT must include a hostname")

        self.endpoint = parsed_endpoint.netloc
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.secure = parsed_endpoint.scheme == "https"
