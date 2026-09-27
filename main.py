import logging

from kafka.handlers.document_uploaded import DocumentUploadedHandler
from kafka.kafka import KafkaClient

logger = logging.getLogger(__name__)
kafka = KafkaClient()


def setup_kafka() -> None:
    logger.info("Kafka initializing")

    document_uploaded_handler = DocumentUploadedHandler(kafka)

    kafka.sub("document.uploaded", document_uploaded_handler.execute)

    logger.info("Kafka initialized")


def main() -> None:
    logger.info("Application started")
    setup_kafka()
    kafka.start()


if __name__ == "__main__":
    main()
