"""
CareerTwin AI – Local File Storage Service
Handles saving uploaded files (PDF, DOCX, TXT) to the local uploads/ folder.
"""

import os
import logging
from fastapi import UploadFile, HTTPException

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Folder constant (mirrors the config value for easy import) ─
UPLOAD_FOLDER = settings.upload_folder


def ensure_upload_folder() -> None:
    """Create the uploads folder if it does not exist."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


async def save_upload_file(file: UploadFile) -> str:
    """
    Save an uploaded file to the local uploads/ directory.

    Args:
        file: FastAPI UploadFile object.

    Returns:
        The full file path where the file was saved.

    Raises:
        HTTPException 400 – if the file type is not allowed.
        HTTPException 413 – if the file exceeds the size limit.
    """
    ensure_upload_folder()

    # ── Validate content type ──────────────────────────────────
    if file.content_type not in settings.allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File type '{file.content_type}' is not allowed. "
                f"Accepted types: {', '.join(settings.allowed_file_types)}"
            ),
        )

    # ── Read file content ──────────────────────────────────────
    content = await file.read()

    # ── Validate file size ─────────────────────────────────────
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds the {settings.max_upload_size_mb} MB limit.",
        )

    # ── Build safe file path and save ─────────────────────────
    safe_filename = os.path.basename(file.filename or "upload.bin")
    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    logger.info(f"File saved: {file_path} ({len(content)} bytes)")
    return file_path


def delete_upload_file(file_path: str) -> None:
    """Delete a previously saved upload file."""
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"File deleted: {file_path}")
    else:
        logger.warning(f"Attempted to delete non-existent file: {file_path}")


def get_file_path(filename: str) -> str:
    """Return the full path for a filename inside the uploads folder."""
    return os.path.join(UPLOAD_FOLDER, os.path.basename(filename))
