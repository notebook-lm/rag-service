import logging
import threading

from config.chunk import RAG_CHUNK_OVERLAP, RAG_CHUNK_SIZE
from config.database import DATABASE_URL
from config.embedding import (
    QWEN3_EMBEDDING_BASE_URL,
    QWEN3_EMBEDDING_DIMENSIONS,
    QWEN3_EMBEDDING_MODEL,
    QWEN3_EMBEDDING_QUERY_INSTRUCTION,
)
from config.grpc import GRPC_PORT
from config.kafka import KAFKA_BOOTSTRAP_SERVERS, KAFKA_CONSUMER_GROUP
from config.rag import RAG_COLLECTION_NAME, RAG_DATABASE_URL
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
from rpc.generated import hello_pb2_grpc, retrieval_pb2_grpc
from rpc.grpc import Grpc
from rpc.rpc import Rpc
from rpc.services.hello_service import HelloService
from rpc.services.retrieval_service import RetrievalService
from rag.chunk.chunk_config import ChunkConfig
from rag.chunk.chunker import Chunker
from rag.chunk.langchain_chunker import LangChainChunker
from rag.embeddings.embedding import Embedding
from rag.embeddings.qwen3_embedding import Qwen3Embedding
from rag.embeddings.qwen3_embedding_config import Qwen3EmbeddingConfig
from rag.langchain_rag import LangChainRag
from rag.parsers.document_parser_factory import DocumentParserFactory
from rag.parsers.excel.openpyxl_excel_parser import OpenPyxlExcelParser
from rag.parsers.office.legacy_office_document_parser import LegacyOfficeDocumentParser
from rag.parsers.pdf.pypdf_pdf_parser import PyPdfPdfParser
from rag.parsers.powerpoint.python_pptx_powerpoint_parser import PythonPptxPowerPointParser
from rag.parsers.text.utf8_text_parser import Utf8TextParser
from rag.parsers.word.python_docx_docx_parser import PythonDocxDocxParser
from rag.rag import Rag
from rag.rag_config import RagConfig
from storage.minio import MinioClient
from storage.minio_config import MinioConfig
from storage.storage import Storage

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
storage: Storage = MinioClient(
    MinioConfig(
        endpoint_url=MINIO_ENDPOINT,
        access_key=MINIO_ROOT_USER,
        secret_key=MINIO_ROOT_PASSWORD,
        bucket=MINIO_BUCKET,
    )
)
pdf_parser = PyPdfPdfParser()
docx_parser = PythonDocxDocxParser()
excel_parser = OpenPyxlExcelParser()
powerpoint_parser = PythonPptxPowerPointParser()
text_parser = Utf8TextParser()
parser_factory = DocumentParserFactory(
    pdf=pdf_parser,
    docx=docx_parser,
    excel=excel_parser,
    powerpoint=powerpoint_parser,
    text=text_parser,
    doc=LegacyOfficeDocumentParser("doc", "docx", docx_parser),
    xls=LegacyOfficeDocumentParser("xls", "xlsx", excel_parser),
    ppt=LegacyOfficeDocumentParser("ppt", "pptx", powerpoint_parser),
)
chunker: Chunker = LangChainChunker(
    ChunkConfig(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
    )
)
embedding: Embedding = Qwen3Embedding(
    Qwen3EmbeddingConfig(
        base_url=QWEN3_EMBEDDING_BASE_URL,
        model=QWEN3_EMBEDDING_MODEL,
        dimensions=QWEN3_EMBEDDING_DIMENSIONS,
        query_instruction=QWEN3_EMBEDDING_QUERY_INSTRUCTION,
    )
)
rag: Rag = LangChainRag(
    RagConfig(
        connection=RAG_DATABASE_URL,
        collection_name=RAG_COLLECTION_NAME,
    ),
    embedding,
)
rpc: Rpc = Grpc(port=GRPC_PORT)

def setup_kafka() -> None:
    logger.info("Kafka initializing")

    document_uploaded_handler = DocumentUploadedHandler(
        messaging,
        database,
        storage,
        parser_factory,
        chunker,
        rag,
    )

    messaging.sub("document.uploaded", document_uploaded_handler.execute)

    logger.info("Kafka initialized")


def setup_grpc() -> None:
    logger.info("gRPC initializing")
    rpc.add_service(
        HelloService(),
        hello_pb2_grpc.add_HelloServiceServicer_to_server,
    )
    rpc.add_service(
        RetrievalService(rag),
        retrieval_pb2_grpc.add_RetrievalServiceServicer_to_server,
    )
    logger.info("gRPC initialized")


def start_kafka() -> None:
    messaging.start()


def start_grpc() -> None:
    rpc.start()


def main() -> None:
    logger.info("Application started")
    setup_kafka()
    setup_grpc()

    kafka_thread = threading.Thread(
        target=start_kafka,
        name="kafka-consumer",
        daemon=True,
    )
    grpc_thread = threading.Thread(
        target=start_grpc,
        name="grpc-server",
        daemon=True,
    )
    kafka_thread.start()
    grpc_thread.start()
    grpc_thread.join()


if __name__ == "__main__":
    main()
