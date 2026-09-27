"""pypdf implementation of PDF parsing."""

from io import BytesIO

from pypdf import PdfReader

from rag.parsers.pdf.pdf_parser import PdfParser


class PyPdfPdfParser(PdfParser):
    """Extract PDF page text with pypdf."""

    def parse(self, content: bytes) -> str:
        reader = PdfReader(BytesIO(content))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()
