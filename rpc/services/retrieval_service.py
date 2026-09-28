"""gRPC service for retrieving document context for chat injection."""

import grpc

from rag.rag import Rag
from rpc.generated import retrieval_pb2, retrieval_pb2_grpc

DEFAULT_LIMIT = 5
MAX_LIMIT = 20
CONTEXT_SEPARATOR = "\n\n---\n\n"


class RetrievalService(retrieval_pb2_grpc.RetrievalServiceServicer):
    """Retrieves semantically relevant, project-scoped document chunks."""

    def __init__(self, rag: Rag) -> None:
        self.rag = rag

    async def RetrieveContext(self, request, context):
        query = request.query.strip()
        project_id = request.project_id.strip()
        document_ids = [document_id.strip() for document_id in request.document_ids if document_id.strip()]

        if not query:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "query must not be blank")
        if not project_id:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "project_id must not be blank")
        if not document_ids:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "document_ids must not be empty")

        limit = request.limit or DEFAULT_LIMIT
        if not 1 <= limit <= MAX_LIMIT:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"limit must be between 1 and {MAX_LIMIT}",
            )

        documents = self.rag.search(
            query,
            {"project_id": project_id, "document_id": {"$in": document_ids}},
            limit,
        )
        chunks = [
            retrieval_pb2.ContextChunk(
                content=document.content,
                document_id=str(document.metadata.get("document_id", "")),
                filename=str(document.metadata.get("filename", "")),
                chunk_index=int(document.metadata.get("chunk_index", 0)),
            )
            for document in documents
        ]
        return retrieval_pb2.RetrieveContextResponse(
            chunks=chunks,
            context=CONTEXT_SEPARATOR.join(chunk.content for chunk in chunks),
        )
