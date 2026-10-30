"""Native PDF text and structural table extraction using PyMuPDF."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import pymupdf


def extract_pdf_content(file_path: Path | str) -> Dict[str, Any]:
    """Extract clean text and structural metadata from a PDF file.

    Args:
        file_path: Absolute or relative path to PDF document.

    Returns:
        Dict with document text, page count, and title metadata.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF document not found: {file_path}")

    doc = pymupdf.open(str(path))
    pages_text = []

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text")
        if text.strip():
            pages_text.append(text.strip())

    full_text = "\n\n".join(pages_text)

    # Basic metadata extraction
    metadata = doc.metadata or {}
    title = metadata.get("title") or path.name

    doc.close()

    return {
        "document_name": path.name,
        "page_count": len(pages_text),
        "text": full_text,
        "title": title,
    }
