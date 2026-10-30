"""Input validation and sanitization for banking queries, uploaded files, and sessions."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Optional, Set, Tuple

ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB
MIN_QUERY_LENGTH: int = 3
MAX_QUERY_LENGTH: int = 2000


def validate_query(
    query: Optional[str],
    min_length: int = MIN_QUERY_LENGTH,
    max_length: int = MAX_QUERY_LENGTH,
) -> Tuple[bool, str]:
    """Validate user banking query string.

    Returns:
        (is_valid, error_message)
    """
    if query is None:
        return False, "Query cannot be null."

    cleaned = query.strip()
    if len(cleaned) < min_length:
        return False, f"Query too short. Minimum length is {min_length} characters."

    if len(cleaned) > max_length:
        return False, f"Query exceeds maximum allowed length of {max_length} characters."

    # Prevent pure non-printable or malicious control characters
    if not any(c.isalnum() for c in cleaned):
        return False, "Query must contain at least one alphanumeric character."

    return True, ""


def validate_uploaded_file(
    file_name: Optional[str],
    file_size_bytes: int,
    allowed_extensions: Optional[Set[str]] = None,
    max_bytes: int = MAX_FILE_SIZE_BYTES,
) -> Tuple[bool, str]:
    """Validate uploaded document filename and size.

    Returns:
        (is_valid, error_message)
    """
    if not file_name:
        return False, "File name cannot be empty."

    allowed = allowed_extensions or ALLOWED_EXTENSIONS
    suffix = Path(file_name).suffix.lower()

    if suffix not in allowed:
        return False, f"Unsupported file type '{suffix}'. Allowed formats: {', '.join(sorted(allowed))}."

    if file_size_bytes <= 0:
        return False, "File is empty (0 bytes)."

    if file_size_bytes > max_bytes:
        max_mb = max_bytes // (1024 * 1024)
        return False, f"File size exceeds maximum threshold of {max_mb} MB."

    return True, ""


def validate_session_id(session_id: Optional[str]) -> bool:
    """Validate if the string is a valid UUID or alphanumeric session key."""
    if not session_id:
        return False
    # Check if standard UUID
    try:
        uuid.UUID(str(session_id))
        return True
    except (ValueError, AttributeError):
        pass
    # Alphanumeric check with hyphens/underscores (length 4 to 64)
    return bool(re.match(r"^[a-zA-Z0-9_-]{4,64}$", str(session_id)))


def sanitize_input_text(text: str) -> str:
    """Strip dangerous control characters while preserving standard punctuation and whitespace."""
    if not text:
        return ""
    # Strip non-printable ASCII except common whitespace (\n, \r, \t)
    cleaned = "".join(ch for ch in text if ch.isprintable() or ch in "\n\r\t")
    return cleaned.strip()
