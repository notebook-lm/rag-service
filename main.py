import logging

from config.database import DATABASE_URL
from config.kafka import KAFKA_BOOTSTRAP_SERVERS, KAFKA_CONSUMER_GROUP
from config.storage import (
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_ROOT_PASSWORD,
    MINIO_ROOT_USER,
)
from database.database import Database
from database.postgres import Postgres
from database.postgres_config import PostgresConfig
from messaging.handlers.document_uploaded import DocumentUploadedHandler
from messaging.kafka import Kafka
from messaging.kafka_config import KafkaConfig
from messaging.messaging import Messaging
from storage.minio import MinioClient
from storage.minio_config import MinioConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)
database: Database = Postgres(PostgresConfig(postgres_url=DATABASE_URL))
messaging: Messaging = Kafka(
    KafkaConfig(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        consumer_group=KAFKA_CONSUMER_GROUP,
    ),
    database,
)
minio = MinioClient(
    MinioConfig(
        endpoint_url=MINIO_ENDPOINT,
        access_key=MINIO_ROOT_USER,
        secret_key=MINIO_ROOT_PASSWORD,
        bucket=MINIO_BUCKET,
    )
)


def setup_kafka() -> None:
    logger.info("Kafka initializing")

    document_uploaded_handler = DocumentUploadedHandler(messaging, database)

    messaging.sub("document.uploaded", document_uploaded_handler.execute)

    logger.info("Kafka initialized")


def main() -> None:
    logger.info("Application started")
    setup_kafka()
    messaging.start()


if __name__ == "__main__":
    main()
