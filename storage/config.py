import os
from urllib.parse import urlparse

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "notebook-lm")


def minio_connection() -> tuple[str, bool]:
    parsed_endpoint = urlparse(MINIO_ENDPOINT)
    if not parsed_endpoint.hostname:
        raise ValueError("MINIO_ENDPOINT must include a hostname")

    endpoint = parsed_endpoint.netloc
    return endpoint, parsed_endpoint.scheme == "https"
