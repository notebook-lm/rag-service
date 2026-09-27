import json


class DocumentUploadedData:
    def __init__(
        self,
        object_key: str,
        project_id: str,
        size_bytes: int,
        document_id: str,
        content_type: str,
        original_filename: str,
    ) -> None:
        self.object_key = object_key
        self.project_id = project_id
        self.size_bytes = size_bytes
        self.document_id = document_id
        self.content_type = content_type
        self.original_filename = original_filename


class DocumentUploadedEvent:
    def __init__(
        self,
        data: DocumentUploadedData,
        event_id: str,
        event_type: str,
        occurred_at: str,
    ) -> None:
        self.data = data
        self.event_id = event_id
        self.event_type = event_type
        self.occurred_at = occurred_at

    def toJson(self) -> bytes:
        return json.dumps(
            {
                "eventId": self.event_id,
                "eventType": self.event_type,
                "occurredAt": self.occurred_at,
                "data": {
                    "objectKey": self.data.object_key,
                    "projectId": self.data.project_id,
                    "sizeBytes": self.data.size_bytes,
                    "documentId": self.data.document_id,
                    "contentType": self.data.content_type,
                    "originalFilename": self.data.original_filename,
                },
            }
        ).encode()
