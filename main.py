import logging

from database.database import Database
from kafka.handlers.document_uploaded import DocumentUploadedHandler
from kafka.kafka import KafkaClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)
database = Database()
kafka = KafkaClient(database)


def setup_kafka() -> None:
    logger.info("Kafka initializing")

    document_uploaded_handler = DocumentUploadedHandler(kafka, database)

    kafka.sub("document.uploaded", document_uploaded_handler.execute)

    logger.info("Kafka initialized")


def main() -> None:
    logger.info("Application started")
    setup_kafka()
    kafka.start()


if __name__ == "__main__":
    main()
