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
