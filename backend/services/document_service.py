"""
CareerTwin AI – Document Processing Service
PDF and DOCX text extraction.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file using PyPDF2.
    Returns concatenated text from all pages.
    """
    try:
        import PyPDF2

        text_parts = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())

        full_text = "\n\n".join(text_parts)
        logger.info(f"PDF extracted: {len(full_text)} chars from {file_path}")
        return full_text

    except Exception as e:
        logger.error(f"PDF extraction failed for {file_path}: {e}")
        raise RuntimeError(f"Failed to extract text from PDF: {e}") from e


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract all text from a DOCX file using python-docx.
    """
    try:
        from docx import Document

        doc = Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        full_text = "\n".join(paragraphs)
        logger.info(f"DOCX extracted: {len(full_text)} chars from {file_path}")
        return full_text

    except Exception as e:
        logger.error(f"DOCX extraction failed for {file_path}: {e}")
        raise RuntimeError(f"Failed to extract text from DOCX: {e}") from e


def extract_text_from_txt(file_path: str) -> str:
    """Read plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text(file_path: str, content_type: str) -> str:
    """
    Route to the correct extractor based on content type.
    Supported: PDF, DOCX, TXT
    """
    if content_type == "application/pdf":
        return extract_text_from_pdf(file_path)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_path)
    elif content_type == "text/plain":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported content type for text extraction: {content_type}")
