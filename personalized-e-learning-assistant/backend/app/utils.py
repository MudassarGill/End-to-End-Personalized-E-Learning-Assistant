"""
Utility Functions - Personalized E-Learning Assistant
File validation, response formatting, text helpers, logging config.
"""

import os
import re
import logging
import functools
import time
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse

logger = logging.getLogger("elearning.utils")


# ═══════════════════════════════════════════════
#  Response Formatters
# ═══════════════════════════════════════════════
def format_response(
    data: Any = None,
    message: str = "Success",
    success: bool = True,
) -> Dict:
    """Consistent API response format."""
    return {
        "success": success,
        "data": data,
        "message": message,
        "error": None,
    }


def format_error(
    error_msg: str,
    status_code: int = 400,
    data: Any = None,
) -> JSONResponse:
    """Consistent error response format."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": data,
            "message": error_msg,
            "error": error_msg,
        },
    )


# ═══════════════════════════════════════════════
#  File Validation
# ═══════════════════════════════════════════════
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".txt", ".md",
    ".pptx", ".csv", ".xlsx", ".xls",
    ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_file(filename: str, file_size: int) -> Dict:
    """
    Validate uploaded file.

    Returns:
        {'valid': True/False, 'error': 'message if invalid'}
    """
    if not filename:
        return {"valid": False, "error": "No filename provided."}

    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        return {
            "valid": False,
            "error": f"Unsupported format: {ext}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        }

    if file_size <= 0:
        return {"valid": False, "error": "File is empty."}

    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        return {
            "valid": False,
            "error": f"File too large: {size_mb:.1f}MB. Max: {MAX_FILE_SIZE // (1024*1024)}MB.",
        }

    return {"valid": True, "error": None}


def get_file_type(filename: str) -> str:
    """Get human-readable file type."""
    ext = Path(filename).suffix.lower()
    types = {
        ".pdf": "PDF Document",
        ".docx": "Word Document",
        ".doc": "Word Document",
        ".txt": "Text File",
        ".md": "Markdown",
        ".pptx": "PowerPoint",
        ".csv": "CSV Spreadsheet",
        ".xlsx": "Excel Spreadsheet",
        ".xls": "Excel Spreadsheet",
        ".png": "PNG Image",
        ".jpg": "JPEG Image",
        ".jpeg": "JPEG Image",
    }
    return types.get(ext, "Unknown")


# ═══════════════════════════════════════════════
#  Text Preprocessing
# ═══════════════════════════════════════════════
def clean_text(text: str) -> str:
    """Clean and normalize text for processing."""
    if not text:
        return ""
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    return text.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split()) if text else 0


def detect_language(text: str) -> str:
    """Detect if text is English or Urdu."""
    urdu_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    total = sum(1 for c in text if c.isalpha())
    if total > 0 and urdu_chars / total > 0.3:
        return "ur"
    return "en"


# ═══════════════════════════════════════════════
#  Decorators
# ═══════════════════════════════════════════════
def timer(func):
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper


def async_timer(func):
    """Async decorator to measure execution time."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper


def safe_execute(default=None):
    """Decorator for safe execution with error catching."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{func.__name__} error: {e}")
                return default
        return wrapper
    return decorator


# ═══════════════════════════════════════════════
#  Config Helpers
# ═══════════════════════════════════════════════
def get_env(key: str, default: str = "") -> str:
    """Get environment variable with fallback."""
    return os.getenv(key, default)


def get_mongo_uri() -> str:
    """Get MongoDB connection URI."""
    return os.getenv(
        "MONGODB_URI",
        "mongodb://localhost:27017",
    )


def get_db_name() -> str:
    """Get database name."""
    return os.getenv("MONGODB_DB", "elearning_db")


# ═══════════════════════════════════════════════
#  Logging Setup
# ═══════════════════════════════════════════════
def setup_logging(level: str = "INFO"):
    """Configure application logging."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    # Quiet noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
