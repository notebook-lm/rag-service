"""RAG configuration."""


class RagConfig:
    def __init__(self, connection: str, collection_name: str) -> None:
        self.connection = connection
        self.collection_name = collection_name
