"""UTF-8 implementation of text parsing."""

from rag.parsers.text.text_parser import TextParser


class Utf8TextParser(TextParser):
    """Decode UTF-8 text and Markdown without changing content."""

    def parse(self, content: bytes) -> str:
        return content.decode("utf-8-sig")
