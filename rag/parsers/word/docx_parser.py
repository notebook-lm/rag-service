"""Abstract DOCX parser contract."""

from rag.parsers.parser import Parser


class DocxParser(Parser):
    """Extract text from DOCX content."""
