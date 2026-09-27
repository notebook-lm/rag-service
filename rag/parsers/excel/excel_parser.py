"""Abstract Excel workbook parser contract."""

from rag.parsers.parser import Parser


class ExcelParser(Parser):
    """Extract text from XLSX workbook content."""
