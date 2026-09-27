"""Qwen3 embedding configuration."""


class Qwen3EmbeddingConfig:
    def __init__(
        self,
        base_url: str,
        model: str,
        dimensions: int,
        query_instruction: str,
    ) -> None:
        self.base_url = base_url
        self.model = model
        self.dimensions = dimensions
        self.query_instruction = query_instruction
