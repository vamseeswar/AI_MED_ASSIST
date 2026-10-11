import os
import re
import hashlib
from typing import Tuple
from fastapi import HTTPException, status
from backend.app.core.config import settings

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    "pdf": ["application/pdf", "application/x-pdf"],
    "docx": [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "application/zip"
    ],
    "txt": ["text/plain", "text/markdown", "application/octet-stream"],
    "csv": ["text/csv", "application/csv", "text/plain", "application/vnd.ms-excel"]
}


def sanitize_filename(filename: str) -> str:
    """Removes path traversal characters and invalid filesystem symbols."""
    # Strip paths
    basename = os.path.basename(filename)
    # Remove directory separators and null bytes
    clean = re.sub(r'[\/\\:\*\?"<>\|\x00]', '_', basename)
    # Remove leading dots to prevent hidden files
    clean = clean.lstrip('.')
    if not clean:
        clean = "uploaded_document"
    return clean


def calculate_file_hash(content: bytes) -> str:
    """Computes SHA-256 hash for document content."""
    sha256 = hashlib.sha256()
    sha256.update(content)
    return sha256.hexdigest()


def validate_file_upload(filename: str, content: bytes, content_type: str = "") -> Tuple[str, int]:
    """Validates file extension, size, and basic MIME integrity."""
    clean_name = sanitize_filename(filename)
    parts = clean_name.rsplit(".", 1)
    if len(parts) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File has no extension. Allowed formats: PDF, DOCX, TXT, CSV."
        )

    extension = parts[1].lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '.{extension}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS).upper()}."
        )

    file_size_bytes = len(content)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    if file_size_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # Magic byte inspection for PDF
    if extension == "pdf" and not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF format: file signature does not match PDF specification."
        )

    return extension, file_size_bytes


def get_safe_storage_path(stored_filename: str) -> str:
    """Returns safe absolute path within STORAGE_DIR, preventing path traversal."""
    storage_root = os.path.abspath(settings.STORAGE_DIR)
    target_path = os.path.abspath(os.path.join(storage_root, stored_filename))
    if not target_path.startswith(storage_root):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Illegal file storage path attempt."
        )
    return target_path
