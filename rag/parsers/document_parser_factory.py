"""Route document types to text parsers."""

from pathlib import Path

from rag.parsers.word.docx_parser import DocxParser
from rag.parsers.excel.excel_parser import ExcelParser
from rag.parsers.parser import Parser
from rag.parsers.pdf.pdf_parser import PdfParser
from rag.parsers.powerpoint.powerpoint_parser import PowerPointParser
from rag.parsers.text.text_parser import TextParser
from rag.parsers.unsupported_document_type_error import UnsupportedDocumentTypeError


class DocumentParserFactory:
    """Select from the document format parsers supplied by the composition root."""

    def __init__(
        self,
        pdf: PdfParser | None = None,
        docx: DocxParser | None = None,
        excel: ExcelParser | None = None,
        powerpoint: PowerPointParser | None = None,
        text: TextParser | None = None,
        doc: Parser | None = None,
        xls: Parser | None = None,
        ppt: Parser | None = None,
    ) -> None:
        self.parsers_by_format = {
            document_format: parser
            for document_format, parser in {
                "pdf": pdf,
                "docx": docx,
                "xlsx": excel,
                "pptx": powerpoint,
                "md": text,
                "markdown": text,
                "txt": text,
                "doc": doc,
                "xls": xls,
                "ppt": ppt,
            }.items()
            if parser is not None
        }
        self.formats_by_extension = {
            ".pdf": "pdf",
            ".docx": "docx",
            ".xlsx": "xlsx",
            ".pptx": "pptx",
            ".md": "md",
            ".markdown": "markdown",
            ".txt": "txt",
            ".doc": "doc",
            ".xls": "xls",
            ".ppt": "ppt",
        }
        self.formats_by_content_type = {
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "application/msword": "doc",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
            "application/vnd.ms-excel": "xls",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
            "application/vnd.ms-powerpoint": "ppt",
            "text/markdown": "md",
            "text/plain": "txt",
        }

    def get_by_content_type(self, content_type: str) -> Parser:
        """Return a parser registered for an exact MIME content type."""
        document_format = self.formats_by_content_type.get(content_type.lower())
        if document_format is None:
            raise UnsupportedDocumentTypeError(f"Unsupported content type: {content_type}")
        return self.get_by_format(document_format)

    def get_by_filename(self, filename: str) -> Parser:
        """Return a parser based on a filename extension."""
        extension = Path(filename).suffix.lower()
        document_format = self.formats_by_extension.get(extension)
        if document_format is None:
            raise UnsupportedDocumentTypeError(f"Unsupported filename: {filename}")
        return self.get_by_format(document_format)

    def get_by_format(self, document_format: str) -> Parser:
        """Return a supplied parser for a format such as `pdf` or `PDF`."""
        parser = self.parsers_by_format.get(document_format.lower())
        if parser is None:
            raise UnsupportedDocumentTypeError(f"No parser configured for format: {document_format}")
        return parser
