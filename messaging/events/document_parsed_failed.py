import json


class DocumentParsedFailedData:
    def __init__(
        self,
        document_id: str,
        project_id: str,
        user_id: str,
        error_code: str,
        error_message: str,
    ) -> None:
        self.document_id = document_id
        self.project_id = project_id
        self.user_id = user_id
        self.error_code = error_code
        self.error_message = error_message


class DocumentParsedFailedEvent:
    def __init__(
        self,
        data: DocumentParsedFailedData,
        event_id: str,
        occurred_at: str,
    ) -> None:
        self.data = data
        self.event_id = event_id
        self.occurred_at = occurred_at

    def toJson(self) -> bytes:
        return json.dumps(
            {
                "eventId": self.event_id,
                "eventType": "document.parsed.failed",
                "occurredAt": self.occurred_at,
                "data": {
                    "documentId": self.data.document_id,
                    "projectId": self.data.project_id,
                    "userId": self.data.user_id,
                    "errorCode": self.data.error_code,
                    "errorMessage": self.data.error_message,
                },
            }
        ).encode()
