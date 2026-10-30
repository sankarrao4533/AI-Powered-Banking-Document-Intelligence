"""Centralized configuration reader for Sentinel Banking Intelligence Backend.

Reads from Streamlit secrets (st.secrets) when running in Streamlit,
or environment variables (.env), providing fallback defaults.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from src.config import settings as src_settings

# Root and directory paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DIR = DATA_DIR / "sample"
BASELINE_DOCS_DIR = DATA_DIR / "baseline_docs"
UPLOADS_DIR = DATA_DIR / "uploads"

# Ensure directories exist
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def get_setting(key: str, default: Optional[Any] = None) -> Any:
    """Retrieve setting from st.secrets if running in Streamlit, else os.environ, else default."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    # Check os.environ
    val = os.getenv(key)
    if val is not None:
        return val.strip().strip('"').strip("'")

    # Fallback to src.config.settings
    if hasattr(src_settings, key):
        return getattr(src_settings, key)

    return default


class BackendSettings:
    """Convenience accessor for backend configuration parameters."""

    @property
    def STORAGE_MODE(self) -> str:
        return str(get_setting("STORAGE_MODE", "auto")).lower()

    @property
    def API_HOST(self) -> str:
        return str(get_setting("API_HOST", "127.0.0.1"))

    @property
    def API_PORT(self) -> int:
        return int(get_setting("API_PORT", 8000))

    @property
    def GROQ_API_KEY(self) -> Optional[str]:
        return get_setting("GROQ_API_KEY", None)

    @property
    def GEMINI_API_KEY(self) -> Optional[str]:
        return get_setting("GEMINI_API_KEY", None)

    @property
    def NEO4J_URI(self) -> str:
        return str(get_setting("NEO4J_URI", "bolt://localhost:7687"))

    @property
    def NEO4J_USER(self) -> str:
        return str(get_setting("NEO4J_USER", "neo4j"))

    @property
    def NEO4J_PASSWORD(self) -> str:
        return str(get_setting("NEO4J_PASSWORD", "password"))

    @property
    def DATA_DIR(self) -> Path:
        return DATA_DIR

    @property
    def SAMPLE_DIR(self) -> Path:
        return SAMPLE_DIR

    @property
    def BASELINE_DOCS_DIR(self) -> Path:
        return BASELINE_DOCS_DIR


backend_settings = BackendSettings()
