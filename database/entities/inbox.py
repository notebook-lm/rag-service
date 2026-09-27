class Inbox:
    def __init__(
        self,
        event_id: str,
        event_type: str,
        topic: str,
        partition: int,
        offset: int,
        payload: bytes,
    ) -> None:
        self.event_id = event_id
        self.event_type = event_type
        self.topic = topic
        self.partition = partition
        self.offset = offset
        self.payload = payload
