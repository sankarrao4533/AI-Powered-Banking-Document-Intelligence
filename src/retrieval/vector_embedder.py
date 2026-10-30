"""Embedding generator with HuggingFace MiniLM and offline fallback."""

from __future__ import annotations

import math
import re
from typing import List, Sequence
import numpy as np

from src.config import settings

_EMBEDDER_INSTANCE = None


class BaseEmbedder:
    """Interface for embedding models."""

    def embed_query(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        raise NotImplementedError


class TransformersEmbedder(BaseEmbedder):
    """Generates dense semantic embeddings using HuggingFace all-MiniLM-L6-v2."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        import os
        import torch
        from transformers import AutoModel, AutoTokenizer

        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["HF_HUB_OFFLINE"] = "1"

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            self.model = AutoModel.from_pretrained(model_name, local_files_only=True)
        except Exception as e:
            raise RuntimeError(f"Local model '{model_name}' not cached offline: {e}") from e

        self.model.eval()

    def _mean_pooling(self, model_output, attention_mask):
        import torch

        token_embeddings = model_output[0]  # First element contains hidden states
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )

    def embed_query(self, text: str) -> List[float]:
        import torch
        import torch.nn.functional as F

        encoded = self.tokenizer(
            [text], padding=True, truncation=True, max_length=512, return_tensors="pt"
        )
        with torch.no_grad():
            outputs = self.model(**encoded)
            pooled = self._mean_pooling(outputs, encoded["attention_mask"])
            normalized = F.normalize(pooled, p=2, dim=1)
            return normalized[0].tolist()

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        import torch
        import torch.nn.functional as F

        if not texts:
            return []
        encoded = self.tokenizer(
            list(texts), padding=True, truncation=True, max_length=512, return_tensors="pt"
        )
        with torch.no_grad():
            outputs = self.model(**encoded)
            pooled = self._mean_pooling(outputs, encoded["attention_mask"])
            normalized = F.normalize(pooled, p=2, dim=1)
            return normalized.tolist()


class FallbackHashEmbedder(BaseEmbedder):
    """Deterministic, lightweight n-gram hashing embedder for offline environments."""

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def _hash_token(self, token: str) -> int:
        h = 2166136261
        for ch in token.lower():
            h = (h ^ ord(ch)) * 16777619
            h &= 0xFFFFFFFF
        return h % self.dimensions

    def embed_query(self, text: str) -> List[float]:
        tokens = re.findall(r"\w+", text.lower())
        vec = np.zeros(self.dimensions, dtype=np.float32)
        if not tokens:
            return vec.tolist()
        for tok in tokens:
            idx = self._hash_token(tok)
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]


def get_embedder() -> BaseEmbedder:
    """Singleton factory returning the best available embedder."""
    global _EMBEDDER_INSTANCE
    if _EMBEDDER_INSTANCE is None:
        try:
            _EMBEDDER_INSTANCE = TransformersEmbedder()
        except Exception as err:
            print(f"[VectorEmbedder] Falling back to offline hash embedder: {err}")
            _EMBEDDER_INSTANCE = FallbackHashEmbedder(settings.EMBEDDING_DIMENSIONS)
    return _EMBEDDER_INSTANCE
