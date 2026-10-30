"""Centralized configuration and environment management for Sentinel Banking GraphRAG."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal
from dotenv import find_dotenv, load_dotenv

# Resolve project root dynamically
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BASELINE_DOCS_DIR = DATA_DIR / "baseline_docs"
SQLITE_DB_PATH = DATA_DIR / "banking_intelligence.db"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
BASELINE_DOCS_DIR.mkdir(parents=True, exist_ok=True)


def load_environment() -> None:
    """Load and sanitize environment variables from .env file and Streamlit secrets."""
    # 1. Sync from Streamlit secrets if running in Streamlit Cloud
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for sec_key in [
                "STORAGE_MODE",
                "GROQ_API_KEY",
                "GEMINI_API_KEY",
                "OPENAI_API_KEY",
                "NEO4J_URI",
                "NEO4J_USER",
                "NEO4J_PASSWORD",
                "API_HOST",
                "API_PORT",
                "MIN_CONFIDENCE_THRESHOLD",
            ]:
                if sec_key in st.secrets and sec_key not in os.environ:
                    val = str(st.secrets[sec_key]).strip()
                    if val:
                        os.environ[sec_key] = val
    except Exception:
        pass

    dotenv_path = find_dotenv(usecwd=True)
    if not dotenv_path:
        # Check standard project root .env
        candidate = PROJECT_ROOT / ".env"
        if candidate.exists():
            dotenv_path = str(candidate)

    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path, override=True)

    # Sanitize quotes and extra whitespaces
    keys_to_clean = [
        "NEO4J_URI",
        "NEO4J_USER",
        "NEO4J_PASSWORD",
        "GROQ_API_KEY",
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "HUGGINGFACE_API_KEY",
        "STORAGE_MODE",
    ]
    for key in keys_to_clean:
        val = os.environ.get(key)
        if val is not None:
            os.environ[key] = val.strip().strip('"').strip("'")


load_environment()

# Standard SME Categories in Enterprise Banking
BANKING_CATEGORIES = (
    "Retail_Loans",
    "Corporate_Banking",
    "KYC_AML",
    "Credit_Cards",
    "Tax_Compliance",
)

TargetCategory = Literal[
    "Retail_Loans",
    "Corporate_Banking",
    "KYC_AML",
    "Credit_Cards",
    "Tax_Compliance",
]


class Settings:
    """Runtime application settings with safe defaults and dynamic environment resolution."""

    # Project metadata
    PROJECT_NAME: str = "Sentinel Banking Document Intelligence"
    VERSION: str = "2.0.0"
    PROJECT_ROOT: Path = PROJECT_ROOT
    DATA_DIR: Path = DATA_DIR
    BASELINE_DOCS_DIR: Path = BASELINE_DOCS_DIR
    SQLITE_DB_PATH: Path = SQLITE_DB_PATH

    # Storage Settings
    @property
    def STORAGE_MODE(self) -> str:
        return os.getenv("STORAGE_MODE", "auto").lower()

    @property
    def NEO4J_URI(self) -> str:
        return os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")

    @property
    def NEO4J_USER(self) -> str:
        return os.getenv("NEO4J_USER", "neo4j")

    @property
    def NEO4J_PASSWORD(self) -> str:
        return os.getenv("NEO4J_PASSWORD", "password")

    # LLM Settings
    @property
    def GROQ_API_KEY(self) -> str | None:
        return os.getenv("GROQ_API_KEY")

    @property
    def GROQ_MODEL(self) -> str:
        return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    @property
    def GEMINI_API_KEY(self) -> str | None:
        return os.getenv("GEMINI_API_KEY")

    @property
    def GEMINI_MODEL(self) -> str:
        return os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    @property
    def OPENAI_API_KEY(self) -> str | None:
        return os.getenv("OPENAI_API_KEY")

    # Embedding Settings
    @property
    def EMBEDDING_MODEL_NAME(self) -> str:
        return os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

    EMBEDDING_DIMENSIONS: int = 384
    TOP_K: int = 5

    # Retrieval & Governance
    @property
    def MIN_CONFIDENCE_THRESHOLD(self) -> float:
        return float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "20.0"))

    # API Settings
    @property
    def API_HOST(self) -> str:
        return os.getenv("API_HOST", "0.0.0.0")

    @property
    def API_PORT(self) -> int:
        return int(os.getenv("API_PORT", "8000"))


settings = Settings()
