"""Hybrid retriever coordinating vector similarity, BM25 keywords, and graph governance."""

from __future__ import annotations

from typing import List, Optional

from src.config import settings
from src.models.schemas import ActivePolicy
from src.retrieval.vector_embedder import get_embedder
from src.storage.base import BaseStorage
from src.storage.factory import get_storage

STRICT_NO_ANSWER = "I cannot find a verified active policy for this in the current database."


class HybridRetriever:
    """Hybrid GraphRAG retriever enforcing active-only governance constraints."""

    def __init__(self, storage: Optional[BaseStorage] = None):
        self.storage = storage or get_storage()
        self.embedder = get_embedder()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_confidence: float = 15.0,
    ) -> List[ActivePolicy]:
        """Perform hybrid retrieval with active policy filtering.

        Args:
            query: User banking question or expanded intent.
            top_k: Number of candidate policies to retrieve.
            min_confidence: Threshold below which results are excluded.

        Returns:
            List[ActivePolicy]: Ranked active policy context nodes.
        """
        if not query or not query.strip():
            return []

        # Generate query dense vector
        query_vec = self.embedder.embed_query(query.strip())

        # Execute hybrid search with supersession firewall
        policies = self.storage.query_active_policies(
            query_text=query.strip(),
            query_embedding=query_vec,
            top_k=top_k,
        )

        # Apply minimum confidence filter
        filtered = [p for p in policies if p.match_confidence >= min_confidence]

        # Additional domain safeguard: if query keywords have zero overlap with any banking policy
        # and match confidence is marginal, discard to prevent false positives
        if filtered and filtered[0].match_confidence < 35.0:
            return []

        return filtered
