"""Storage factory for selecting between Neo4j and Embedded storage engines."""

from __future__ import annotations

import os
from src.config import settings
from src.storage.base import BaseStorage
from src.storage.embedded_backend import EmbeddedStorageBackend

_STORAGE_INSTANCE: BaseStorage | None = None


def get_storage(force_refresh: bool = False) -> BaseStorage:
    """Return the active storage backend.

    Modes:
    - 'neo4j': Strictly use Neo4j (raises error if unreachable).
    - 'embedded': Strictly use embedded NetworkX + SQLite.
    - 'auto' (default): Try connecting to Neo4j. If unavailable, smoothly use embedded.
    """
    global _STORAGE_INSTANCE
    if _STORAGE_INSTANCE is not None and not force_refresh:
        return _STORAGE_INSTANCE

    mode = settings.STORAGE_MODE

    if mode == "neo4j":
        from src.storage.neo4j_backend import Neo4jStorageBackend
        print(f"[StorageFactory] Initializing strict Neo4j backend ({settings.NEO4J_URI})...")
        _STORAGE_INSTANCE = Neo4jStorageBackend()
        return _STORAGE_INSTANCE

    if mode == "embedded":
        print(f"[StorageFactory] Initializing embedded backend ({settings.SQLITE_DB_PATH})...")
        _STORAGE_INSTANCE = EmbeddedStorageBackend()
        return _STORAGE_INSTANCE

    # Auto mode: attempt Neo4j first, fall back to embedded
    try:
        from src.storage.neo4j_backend import Neo4jStorageBackend
        backend = Neo4jStorageBackend()
        print("[StorageEngine] Active: Enterprise Neo4j Backend (bolt://127.0.0.1:7687)")
        _STORAGE_INSTANCE = backend
        return _STORAGE_INSTANCE
    except Exception:
        print("[StorageEngine] Active: Embedded Knowledge Graph (NetworkX + SQLite)")
        _STORAGE_INSTANCE = EmbeddedStorageBackend()
        return _STORAGE_INSTANCE
