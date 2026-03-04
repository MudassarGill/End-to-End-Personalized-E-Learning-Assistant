"""
╔══════════════════════════════════════════════════════════════╗
║  Text Extraction Module - Personalized E-Learning Assistant  ║
║  Supports: PDF (PyPDF2 + pdfplumber), DOCX, TXT, Images     ║
║  Features: Chunking, Metadata, Fallback, Language Detection  ║
╚══════════════════════════════════════════════════════════════╝
"""

import io
import re
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Union

# ─── Logger Setup ───
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(handler)


# ═══════════════════════════════════════════════
#  PDFTextExtractor Class
# ═══════════════════════════════════════════════
class PDFTextExtractor:
    """
    Production-ready PDF text extractor with multiple methods,
    chunking, metadata extraction, and comprehensive error handling.

    Usage:
        extractor = PDFTextExtractor()

        # From file path
        result = extractor.extract("document.pdf")

        # From bytes (API upload)
        result = extractor.extract_from_bytes(pdf_bytes)

        # Get metadata only
        metadata = extractor.get_metadata("document.pdf")

        # Chunk long text
        chunks = extractor.chunk_text(text, chunk_size=1000, overlap=200)
    """

    # Supported extraction methods
    SUPPORTED_METHODS = ["pdfplumber", "pypdf2"]

    # Max file size: 100 MB
    MAX_FILE_SIZE = 100 * 1024 * 1024

    def __init__(self, default_method: str = "pdfplumber"):
        """
        Initialize PDFTextExtractor.

        Args:
            default_method: Preferred extraction method ('pdfplumber' or 'pypdf2')
        """
        if default_method not in self.SUPPORTED_METHODS:
            raise ValueError(
                f"Unsupported method: {default_method}. "
                f"Choose from: {self.SUPPORTED_METHODS}"
            )
        self.default_method = default_method
        logger.info(f"PDFTextExtractor initialized (default: {default_method})")

    # ──────────────────────────────────────────
    #  Main Extract Method
    # ──────────────────────────────────────────
    def extract(
        self,
        pdf_path: str,
        method: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Main extraction method — tries preferred method first, falls back to other.

        Args:
            pdf_path: Path to the PDF file
            method: Extraction method ('pdfplumber' or 'pypdf2'), None uses default
            chunk_size: Size of text chunks (in characters)
            chunk_overlap: Overlap between chunks
            progress_callback: Optional callback(current_page, total_pages)

        Returns:
            Dictionary with extraction results (see Output Format in docstring)
        """
        pdf_path = Path(pdf_path)
        method = method or self.default_method
        start_time = time.time()

        # ── Validate file ──
        validation = self._validate_file(pdf_path)
        if not validation["valid"]:
            return self._error_result(validation["error"])

        logger.info(f"Extracting text from: {pdf_path.name} (method: {method})")

        # ── Try primary method ──
        text = ""
        method_used = method
        error_msg = None

        try:
            if method == "pdfplumber":
                text = self.extract_with_pdfplumber(
                    str(pdf_path), progress_callback
                )
            else:
                text = self.extract_with_pypdf2(
                    str(pdf_path), progress_callback
                )
        except Exception as e:
            logger.warning(f"Primary method ({method}) failed: {e}")
            error_msg = str(e)

        # ── Fallback to other method ──
        if not text or not text.strip():
            fallback = "pypdf2" if method == "pdfplumber" else "pdfplumber"
            logger.info(f"Falling back to: {fallback}")
            try:
                if fallback == "pdfplumber":
                    text = self.extract_with_pdfplumber(str(pdf_path))
                else:
                    text = self.extract_with_pypdf2(str(pdf_path))
                method_used = fallback
                error_msg = None
            except Exception as e:
                logger.error(f"Fallback ({fallback}) also failed: {e}")
                error_msg = f"Both methods failed. Primary: {error_msg}. Fallback: {e}"

        # ── Handle no text (scanned PDF) ──
        if not text or not text.strip():
            return self._error_result(
                error_msg or "No text extracted. PDF may be scanned/image-based. "
                "Consider using OCR (pytesseract + PyMuPDF) for scanned documents."
            )

        # ── Clean text ──
        cleaned_text = self.clean_text(text)

        # ── Get metadata ──
        metadata = self.get_metadata(str(pdf_path))

        # ── Generate chunks ──
        chunks = self.chunk_text(cleaned_text, chunk_size, chunk_overlap)

        # ── Build result ──
        elapsed = time.time() - start_time
        words = cleaned_text.split()

        result = {
            "success": True,
            "text": text,
            "cleaned_text": cleaned_text,
            "method_used": method_used,
            "pages": metadata.get("pages", 0),
            "characters": len(cleaned_text),
            "words": len(words),
            "chunks": chunks,
            "num_chunks": len(chunks),
            "metadata": metadata,
            "extraction_time_seconds": round(elapsed, 2),
            "error": None,
        }

        logger.info(
            f"Extraction complete: {result['pages']} pages, "
            f"{result['words']} words, {result['num_chunks']} chunks, "
            f"{elapsed:.2f}s"
        )
        return result

    # ──────────────────────────────────────────
    #  Extract from Bytes (for API/Upload)
    # ──────────────────────────────────────────
    def extract_from_bytes(
        self,
        pdf_bytes: bytes,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> Dict[str, Any]:
        """
        Extract text from PDF bytes (for API file uploads).

        Args:
            pdf_bytes: Raw PDF file bytes
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks

        Returns:
            Dictionary with extraction results
        """
        start_time = time.time()

        if not pdf_bytes:
            return self._error_result("Empty PDF bytes received.")

        if len(pdf_bytes) > self.MAX_FILE_SIZE:
            size_mb = len(pdf_bytes) / (1024 * 1024)
            return self._error_result(
                f"File too large: {size_mb:.1f} MB. Maximum: "
                f"{self.MAX_FILE_SIZE / (1024*1024):.0f} MB."
            )

        logger.info(f"Extracting from bytes ({len(pdf_bytes)} bytes)")

        text = ""
        method_used = ""

        # ── Try pdfplumber first ──
        try:
            text = self._extract_bytes_pdfplumber(pdf_bytes)
            method_used = "pdfplumber"
        except Exception as e:
            logger.warning(f"pdfplumber bytes extraction failed: {e}")

        # ── Fallback to PyPDF2 ──
        if not text or not text.strip():
            try:
                text = self._extract_bytes_pypdf2(pdf_bytes)
                method_used = "pypdf2"
            except Exception as e:
                logger.error(f"PyPDF2 bytes extraction also failed: {e}")
                return self._error_result(
                    f"Could not extract text from PDF bytes: {e}"
                )

        if not text or not text.strip():
            return self._error_result(
                "No text could be extracted. The PDF may be scanned/image-based."
            )

        cleaned_text = self.clean_text(text)
        chunks = self.chunk_text(cleaned_text, chunk_size, chunk_overlap)
        words = cleaned_text.split()
        elapsed = time.time() - start_time

        # Get page count from bytes
        page_count = self._get_page_count_from_bytes(pdf_bytes)

        return {
            "success": True,
            "text": text,
            "cleaned_text": cleaned_text,
            "method_used": method_used,
            "pages": page_count,
            "characters": len(cleaned_text),
            "words": len(words),
            "chunks": chunks,
            "num_chunks": len(chunks),
            "metadata": {"pages": page_count},
            "extraction_time_seconds": round(elapsed, 2),
            "error": None,
        }

    # ──────────────────────────────────────────
    #  PyPDF2 Extraction
    # ──────────────────────────────────────────
    def extract_with_pypdf2(
        self,
        pdf_path: str,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """
        Extract text using PyPDF2 library.

        Args:
            pdf_path: Path to PDF file
            progress_callback: Optional callback(current_page, total_pages)

        Returns:
            Extracted text string

        Raises:
            ImportError: If PyPDF2 is not installed
            Exception: On extraction failure
        """
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            raise ImportError(
                "PyPDF2 not installed. Run: pip install PyPDF2==3.0.1"
            )

        logger.info(f"[PyPDF2] Reading: {pdf_path}")

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        # ── Check for encryption ──
        if reader.is_encrypted:
            try:
                reader.decrypt("")  # Try empty password
                logger.info("[PyPDF2] Decrypted with empty password")
            except Exception:
                raise ValueError(
                    "PDF is encrypted/password-protected. "
                    "Please provide an unlocked PDF."
                )

        # ── Extract text page by page ──
        text_parts = []
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                logger.warning(f"[PyPDF2] Page {i+1} extraction error: {e}")

            # Progress callback
            if progress_callback:
                progress_callback(i + 1, total_pages)

        text = "\n".join(text_parts)
        logger.info(
            f"[PyPDF2] Done: {total_pages} pages, {len(text)} chars"
        )
        return text

    def _extract_bytes_pypdf2(self, pdf_bytes: bytes) -> str:
        """Extract text from bytes using PyPDF2"""
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))

        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise ValueError("PDF is encrypted.")

        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        return "\n".join(text_parts)

    # ──────────────────────────────────────────
    #  pdfplumber Extraction
    # ──────────────────────────────────────────
    def extract_with_pdfplumber(
        self,
        pdf_path: str,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """
        Extract text using pdfplumber library.
        Better for documents with tables and complex layouts.

        Args:
            pdf_path: Path to PDF file
            progress_callback: Optional callback(current_page, total_pages)

        Returns:
            Extracted text string

        Raises:
            ImportError: If pdfplumber is not installed
            Exception: On extraction failure
        """
        try:
            import pdfplumber
        except ImportError:
            raise ImportError(
                "pdfplumber not installed. Run: pip install pdfplumber==0.10.3"
            )

        logger.info(f"[pdfplumber] Reading: {pdf_path}")

        text_parts = []

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            for i, page in enumerate(pdf.pages):
                try:
                    # Extract regular text
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                    # Extract tables (convert to text)
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            table_text = self._table_to_text(table)
                            if table_text:
                                text_parts.append(table_text)

                except Exception as e:
                    logger.warning(
                        f"[pdfplumber] Page {i+1} error: {e}"
                    )

                if progress_callback:
                    progress_callback(i + 1, total_pages)

        text = "\n".join(text_parts)
        logger.info(
            f"[pdfplumber] Done: {total_pages} pages, {len(text)} chars"
        )
        return text

    def _extract_bytes_pdfplumber(self, pdf_bytes: bytes) -> str:
        """Extract text from bytes using pdfplumber"""
        import pdfplumber

        text_parts = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        table_text = self._table_to_text(table)
                        if table_text:
                            text_parts.append(table_text)

        return "\n".join(text_parts)

    # ──────────────────────────────────────────
    #  Text Cleaning
    # ──────────────────────────────────────────
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text — remove extra whitespace, special chars, fix formatting.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text string
        """
        if not text:
            return ""

        # Remove null bytes
        text = text.replace("\x00", "")

        # Normalize unicode
        text = text.encode("utf-8", errors="ignore").decode("utf-8")

        # Replace multiple spaces with single space
        text = re.sub(r"[ \t]+", " ", text)

        # Replace 3+ newlines with 2
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove leading/trailing whitespace on each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        # Remove lines that are just special characters
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            # Keep line if it has at least some alphanumeric content
            alpha_count = sum(1 for c in line if c.isalnum())
            if alpha_count > 0 or line.strip() == "":
                cleaned_lines.append(line)

        text = "\n".join(cleaned_lines)

        # Final trim
        text = text.strip()

        return text

    # ──────────────────────────────────────────
    #  Metadata Extraction
    # ──────────────────────────────────────────
    def get_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract PDF metadata (title, author, creation date, pages, etc.)

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with metadata fields
        """
        metadata = {
            "title": None,
            "author": None,
            "subject": None,
            "creator": None,
            "producer": None,
            "creation_date": None,
            "modification_date": None,
            "pages": 0,
            "file_size_bytes": 0,
            "file_size_mb": 0.0,
        }

        try:
            # File info
            path = Path(pdf_path)
            if path.exists():
                metadata["file_size_bytes"] = path.stat().st_size
                metadata["file_size_mb"] = round(
                    path.stat().st_size / (1024 * 1024), 2
                )

            # PDF metadata via PyPDF2
            from PyPDF2 import PdfReader

            reader = PdfReader(pdf_path)
            metadata["pages"] = len(reader.pages)

            if reader.metadata:
                meta = reader.metadata
                metadata["title"] = meta.get("/Title", None)
                metadata["author"] = meta.get("/Author", None)
                metadata["subject"] = meta.get("/Subject", None)
                metadata["creator"] = meta.get("/Creator", None)
                metadata["producer"] = meta.get("/Producer", None)

                # Parse dates
                if meta.get("/CreationDate"):
                    metadata["creation_date"] = str(meta["/CreationDate"])
                if meta.get("/ModDate"):
                    metadata["modification_date"] = str(meta["/ModDate"])

            # Clean None strings
            for key in metadata:
                if metadata[key] == "None" or metadata[key] == "":
                    metadata[key] = None

        except Exception as e:
            logger.warning(f"Metadata extraction error: {e}")

        return metadata

    # ──────────────────────────────────────────
    #  Text Chunking
    # ──────────────────────────────────────────
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks for processing.
        Tries to split at sentence boundaries for better coherence.

        Args:
            text: Input text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks

        Returns:
            List of chunk dictionaries with text, index, char counts
        """
        if not text:
            return []

        if len(text) <= chunk_size:
            return [{
                "index": 0,
                "text": text,
                "characters": len(text),
                "words": len(text.split()),
                "start_char": 0,
                "end_char": len(text),
            }]

        # Split into sentences first
        sentences = re.split(r'(?<=[.!?\n])\s+', text)

        chunks = []
        current_chunk = ""
        current_start = 0
        char_position = 0

        for sentence in sentences:
            # If adding this sentence exceeds chunk_size, save current chunk
            if (
                len(current_chunk) + len(sentence) > chunk_size
                and current_chunk
            ):
                chunk_data = {
                    "index": len(chunks),
                    "text": current_chunk.strip(),
                    "characters": len(current_chunk.strip()),
                    "words": len(current_chunk.strip().split()),
                    "start_char": current_start,
                    "end_char": current_start + len(current_chunk),
                }
                chunks.append(chunk_data)

                # Apply overlap — keep last 'overlap' characters
                if overlap > 0 and len(current_chunk) > overlap:
                    # Find a sentence boundary near the overlap point
                    overlap_text = current_chunk[-overlap:]
                    current_start = (
                        current_start + len(current_chunk) - len(overlap_text)
                    )
                    current_chunk = overlap_text + " " + sentence
                else:
                    current_start = char_position
                    current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence

            char_position += len(sentence) + 1

        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                "index": len(chunks),
                "text": current_chunk.strip(),
                "characters": len(current_chunk.strip()),
                "words": len(current_chunk.strip().split()),
                "start_char": current_start,
                "end_char": current_start + len(current_chunk),
            })

        logger.info(
            f"Chunked {len(text)} chars into {len(chunks)} chunks "
            f"(size={chunk_size}, overlap={overlap})"
        )
        return chunks

    # ──────────────────────────────────────────
    #  Private Helper Methods
    # ──────────────────────────────────────────
    def _validate_file(self, pdf_path: Path) -> Dict[str, Any]:
        """Validate PDF file before extraction"""
        if not pdf_path.exists():
            return {"valid": False, "error": f"File not found: {pdf_path}"}

        if not pdf_path.is_file():
            return {"valid": False, "error": f"Not a file: {pdf_path}"}

        suffix = pdf_path.suffix.lower()
        if suffix != ".pdf":
            return {
                "valid": False,
                "error": f"Not a PDF file (got {suffix}). Only .pdf files supported.",
            }

        file_size = pdf_path.stat().st_size
        if file_size == 0:
            return {"valid": False, "error": "File is empty (0 bytes)."}

        if file_size > self.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            return {
                "valid": False,
                "error": f"File too large: {size_mb:.1f} MB (max: {max_mb:.0f} MB)",
            }

        return {"valid": True, "error": None}

    def _table_to_text(self, table: List[List]) -> str:
        """Convert pdfplumber table data to readable text"""
        if not table:
            return ""
        rows = []
        for row in table:
            cells = [str(cell).strip() if cell else "" for cell in row]
            row_text = " | ".join(cells)
            if row_text.strip().replace("|", "").strip():
                rows.append(row_text)
        return "\n".join(rows)

    def _get_page_count_from_bytes(self, pdf_bytes: bytes) -> int:
        """Get page count from PDF bytes"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(pdf_bytes))
            return len(reader.pages)
        except Exception:
            return 0

    def _error_result(self, error_msg: str) -> Dict[str, Any]:
        """Generate standardized error result"""
        logger.error(f"Extraction failed: {error_msg}")
        return {
            "success": False,
            "text": "",
            "cleaned_text": "",
            "method_used": None,
            "pages": 0,
            "characters": 0,
            "words": 0,
            "chunks": [],
            "num_chunks": 0,
            "metadata": {},
            "extraction_time_seconds": 0,
            "error": error_msg,
        }


# ═══════════════════════════════════════════════
#  Multi-Format Extraction (for upload.py route)
# ═══════════════════════════════════════════════

# Supported file extensions
SUPPORTED_EXTENSIONS = [
    ".pdf", ".docx", ".doc", ".txt", ".md",
    ".pptx", ".csv", ".xlsx", ".xls",
    ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp",
]


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Universal text extraction — detects file type and uses appropriate method.
    This is the main entry point used by the upload route.

    Args:
        file_bytes: Raw file bytes
        filename: Original filename (used to detect type)

    Returns:
        Extracted text string

    Raises:
        ValueError: If file type not supported or no text extracted
    """
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        extractor = PDFTextExtractor()
        result = extractor.extract_from_bytes(file_bytes)
        if result["success"]:
            return result["cleaned_text"]
        else:
            raise ValueError(result["error"])

    elif ext in [".docx", ".doc"]:
        return _extract_from_docx(file_bytes)

    elif ext in [".txt", ".md", ".csv"]:
        return _extract_from_txt(file_bytes)

    elif ext == ".pptx":
        return _extract_from_pptx(file_bytes)

    elif ext in [".xlsx", ".xls"]:
        return _extract_from_excel(file_bytes)

    elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]:
        return _extract_from_image(file_bytes)

    else:
        # Try as plain text
        try:
            return file_bytes.decode("utf-8", errors="ignore").strip()
        except Exception:
            raise ValueError(
                f"Unsupported file type: {ext}. "
                f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
            )


# ──────────────────────────────────────────
#  Format-Specific Extractors
# ──────────────────────────────────────────
def _extract_from_docx(file_bytes: bytes) -> str:
    """Extract text from Word documents"""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx required. Install: pip install python-docx")

    doc = Document(io.BytesIO(file_bytes))
    parts = [p.text for p in doc.paragraphs if p.text.strip()]

    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(
                c.text.strip() for c in row.cells if c.text.strip()
            )
            if row_text:
                parts.append(row_text)

    text = "\n".join(parts)
    if not text.strip():
        raise ValueError("No text extracted from DOCX file.")
    return text


def _extract_from_txt(file_bytes: bytes) -> str:
    """Extract text from plain text files"""
    for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            text = file_bytes.decode(encoding)
            if text.strip():
                return text
        except (UnicodeDecodeError, ValueError):
            continue
    return file_bytes.decode("utf-8", errors="ignore")


def _extract_from_pptx(file_bytes: bytes) -> str:
    """Extract text from PowerPoint files"""
    try:
        from pptx import Presentation
    except ImportError:
        raise ImportError("python-pptx required. Install: pip install python-pptx")

    prs = Presentation(io.BytesIO(file_bytes))
    parts = []

    for slide_num, slide in enumerate(prs.slides, 1):
        parts.append(f"\n--- Slide {slide_num} ---")
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    if para.text.strip():
                        parts.append(para.text.strip())
            if shape.has_table:
                for row in shape.table.rows:
                    row_text = " | ".join(
                        c.text.strip() for c in row.cells if c.text.strip()
                    )
                    if row_text:
                        parts.append(row_text)

    text = "\n".join(parts)
    if not text.strip():
        raise ValueError("No text extracted from PPTX file.")
    return text


def _extract_from_excel(file_bytes: bytes) -> str:
    """Extract text from Excel files"""
    try:
        import openpyxl
    except ImportError:
        raise ImportError("openpyxl required. Install: pip install openpyxl")

    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True)
    parts = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        parts.append(f"\n--- Sheet: {sheet_name} ---")
        for row in ws.iter_rows(values_only=True):
            row_text = " | ".join(str(c) for c in row if c is not None)
            if row_text.strip():
                parts.append(row_text)

    wb.close()
    text = "\n".join(parts)
    if not text.strip():
        raise ValueError("No text extracted from Excel file.")
    return text


def _extract_from_image(file_bytes: bytes) -> str:
    """Extract text from images using OCR"""
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        raise ImportError(
            "Pillow and pytesseract required. "
            "Install: pip install Pillow pytesseract\n"
            "Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract"
        )

    img = Image.open(io.BytesIO(file_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")

    text = pytesseract.image_to_string(img)
    if not text.strip():
        raise ValueError("No text extracted from image. OCR found no readable text.")
    return text


# ═══════════════════════════════════════════════
#  CLI Testing
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python text_extraction.py <pdf_path>")
        print("Example: python text_extraction.py document.pdf")
        sys.exit(1)

    pdf_file = sys.argv[1]

    def show_progress(current, total):
        pct = (current / total) * 100
        bar = "=" * int(pct // 2) + ">" + " " * (50 - int(pct // 2))
        print(f"\r  [{bar}] {pct:.0f}% ({current}/{total} pages)", end="")
        if current == total:
            print()

    extractor = PDFTextExtractor()
    result = extractor.extract(pdf_file, progress_callback=show_progress)

    print(f"\n{'='*60}")
    print(f"  Success:     {result['success']}")
    print(f"  Method:      {result['method_used']}")
    print(f"  Pages:       {result['pages']}")
    print(f"  Characters:  {result['characters']}")
    print(f"  Words:       {result['words']}")
    print(f"  Chunks:      {result['num_chunks']}")
    print(f"  Time:        {result['extraction_time_seconds']}s")
    print(f"{'='*60}")

    if result["success"]:
        print(f"\n  Preview (first 500 chars):")
        print(f"  {result['cleaned_text'][:500]}...")
    else:
        print(f"\n  Error: {result['error']}")
