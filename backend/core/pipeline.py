"""End-to-end GraphRAG pipeline orchestrating parsing, governance, retrieval, and scoring."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.utils.validators import sanitize_input_text, validate_query
from src.copilot.agent import CopilotAgent
from src.copilot.prompt_enhancer import enhance_banking_query
from src.ingestion.curator import CuratorPipeline
from src.models.schemas import ActivePolicy, ChatResponse, IngestionResponse, PolicyRecord
from src.retrieval.hybrid_retriever import HybridRetriever
from src.storage.base import BaseStorage
from src.storage.factory import get_storage


class BankingIntelligencePipeline:
    """Project-specific pipeline orchestrating document ingestion, GraphRAG retrieval, and scoring."""

    def __init__(self, storage: Optional[BaseStorage] = None):
        self.storage = storage or get_storage()
        self.retriever = HybridRetriever(self.storage)
        self.agent = CopilotAgent(self.storage)
        self.curator = CuratorPipeline(self.storage)

    def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        enhance: bool = True,
    ) -> ChatResponse:
        """Validate input query, optionally enhance acronyms, retrieve active rules, and synthesize answer."""
        is_valid, err_msg = validate_query(query)
        if not is_valid:
            return ChatResponse(
                session_id=session_id or "error_session",
                response=f"Validation Error: {err_msg}",
                citations=[],
                confidence_score=0.0,
                governance_status="VALIDATION_FAILED",
                enhanced_query=None,
            )

        sanitized_query = sanitize_input_text(query)
        return self.agent.answer_question(
            user_question=sanitized_query,
            session_id=session_id,
            enhance_query=enhance,
        )

    def ingest_document(self, file_path: Path | str) -> IngestionResponse:
        """Parse regulatory document, detect supersessions, and commit to knowledge graph."""
        return self.curator.ingest_file(file_path)

    def list_active_policies(self) -> List[PolicyRecord]:
        """Fetch all verified active policies from storage."""
        return [p for p in self.storage.get_all_policies() if p.active]

    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Compute pipeline health, total nodes, and supersession statistics."""
        policies = self.storage.get_all_policies()
        active = sum(1 for p in policies if p.active)
        return {
            "total_policies": len(policies),
            "active_policies": active,
            "superseded_policies": len(policies) - active,
            "storage_backend": type(self.storage).__name__,
        }
