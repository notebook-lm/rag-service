# RAG Service

The service parses uploaded documents, splits them into chunks, and stores their embeddings in PGVector. Each indexed chunk carries `project_id` and `document_id` metadata inherited from the `document.uploaded` event.

## Scoped semantic retrieval

Use `search(query, filters, limit)` to retrieve chunks. The RAG adapter forwards `filters` to PGVector as a JSONB metadata filter, so services can compose the scope they need.

```python
# All matching chunks that belong to one project.
project_chunks = rag.search(
    "What are the payment terms?",
    filters={"project_id": "project-123"},
    limit=5,
)

# Matching chunks from selected documents in that project.
document_chunks = rag.search(
    "What are the payment terms?",
    filters={
        "project_id": "project-123",
        "document_id": {"$in": ["document-456", "document-789"]},
    },
    limit=5,
)
```

Always include `project_id` in the filters passed by an integrating service. This prevents chunks from unrelated projects from entering the candidate set.

## gRPC Hello World

The service also exposes an async gRPC endpoint on port `50051`:

```text
notebooklm.rag.v1.HelloService/SayHello
```

Regenerate Python bindings after changing a file in `proto/`:

```bash
uv run python scripts/generate_proto.py
```

Start the service with Docker Compose, then call it from the project environment:

```bash
uv run python - <<'PY'
import asyncio
import grpc
from rpc.generated import hello_pb2, hello_pb2_grpc

async def main():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        client = hello_pb2_grpc.HelloServiceStub(channel)
        response = await client.SayHello(hello_pb2.HelloRequest(name="An"))
        print(response.message)

asyncio.run(main())
PY
```

Expected output:

```text
Hello, An!
```
