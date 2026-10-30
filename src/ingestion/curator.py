"""Curator agent pipeline for ingesting banking documents into the knowledge graph."""

from __future__ import annotations

import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.config import settings
from src.ingestion.multimodal_extractor import (
    extract_offline_heuristic,
    extract_with_gemini,
    extract_with_groq,
)
from src.ingestion.pdf_parser import extract_pdf_content
from src.models.schemas import GraphAction, IngestionResponse, PolicyRecord
from src.retrieval.vector_embedder import get_embedder
from src.storage.base import BaseStorage
from src.storage.factory import get_storage


class CuratorPipeline:
    """Enterprise curator agent managing document ingestion and supersession lineage."""

    def __init__(self, storage: Optional[BaseStorage] = None):
        self.storage = storage or get_storage()
        self.embedder = get_embedder()

    def ingest_file(
        self,
        file_path: Path | str,
        override_text: Optional[str] = None,
        override_action: Optional[GraphAction] = None,
    ) -> IngestionResponse:
        """Process a single PDF or image file and persist into the knowledge graph."""
        path = Path(file_path)
        doc_name = path.name

        text_content = override_text or ""
        mime_type, _ = mimetypes.guess_type(str(path))
        mime_type = mime_type or ("application/pdf" if path.suffix.lower() == ".pdf" else "image/png")

        # 1. Parse content
        if not text_content:
            if path.suffix.lower() == ".pdf":
                pdf_data = extract_pdf_content(path)
                text_content = pdf_data["text"]
            elif path.suffix.lower() in (".png", ".jpg", ".jpeg"):
                # Table charts have meaningful metadata in filenames
                text_content = f"Regulatory Table: {doc_name}. Details extracted from visual banking matrix."

        # 2. Extract structured GraphAction
        action = override_action
        if action is None:
            # Try Gemini Multimodal first (ideal for visual PNG tables and PDFs)
            action = extract_with_gemini(path, mime_type=mime_type)

            # Fall back to Groq LLM if text is available
            if action is None and text_content:
                action = extract_with_groq(text_content, doc_name)

            # Fall back to offline heuristic extractor
            if action is None:
                action = extract_offline_heuristic(doc_name, text_content)

        # 3. Generate dense semantic embedding
        semantic_search_text = f"{doc_name}\nCategory: {action.target_node}\nRule: {action.extracted_rule}\n\n{text_content}"
        embedding = self.embedder.embed_query(semantic_search_text)

        # 4. Construct Policy Record
        issue_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if "2024" in doc_name:
            issue_date = "2024-01-01"
        elif "2025" in doc_name:
            issue_date = "2025-01-01"
        elif "2026" in doc_name:
            issue_date = "2026-01-01"

        policy = PolicyRecord(
            name=doc_name,
            category=action.target_node,
            issue_date=issue_date,
            source_text=text_content,
            extracted_rule=action.extracted_rule,
            action_type=action.action_type,
            active=True,
            superseded_by=None,
            supersedes=action.superseded_document,
            applies_to_customer=action.applies_to_customer,
            requires_document=action.requires_document,
            embedding=embedding,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        # 5. Persist into knowledge graph
        self.storage.save_policy(policy)

        # 6. Apply supersession firewall link if required
        if action.action_type == "SUPERSEDE_OLD" and action.superseded_document:
            self.storage.supersede_policy(
                new_policy_name=doc_name,
                old_policy_name=action.superseded_document,
            )
            print(f"[Curator] Linked supersession: {doc_name} SUPERSEDES {action.superseded_document}")

        return IngestionResponse(
            document_name=doc_name,
            category=action.target_node,
            action_type=action.action_type,
            extracted_rule=action.extracted_rule,
            superseded_document=action.superseded_document,
            applies_to_customer=action.applies_to_customer,
            requires_document=action.requires_document,
            status="SUCCESS",
            message=f"Document '{doc_name}' successfully indexed in {action.target_node}.",
        )
