"""Abstract plain-text parser contract."""

from rag.parsers.parser import Parser


class TextParser(Parser):
    """Extract text from plain-text or Markdown content."""
