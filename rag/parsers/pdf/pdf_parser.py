"""Abstract PDF parser contract."""

from rag.parsers.parser import Parser


class PdfParser(Parser):
    """Extract text from PDF content."""
