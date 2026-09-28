import json


class DocumentProcessingData:
    def __init__(
        self,
        document_id: str,
        project_id: str,
        user_id: str,
        status: str,
    ) -> None:
        self.document_id = document_id
        self.project_id = project_id
        self.user_id = user_id
        self.status = status


class DocumentProcessingEvent:
    def __init__(
        self,
        data: DocumentProcessingData,
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
                    "documentId": self.data.document_id,
                    "projectId": self.data.project_id,
                    "userId": self.data.user_id,
                    "status": self.data.status,
                },
            }
        ).encode()
