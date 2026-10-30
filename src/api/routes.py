"""FastAPI route controllers for Sentinel Banking Copilot and Ingestion APIs."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.copilot.agent import CopilotAgent
from src.copilot.prompt_enhancer import enhance_banking_query
from src.ingestion.curator import CuratorPipeline
from src.models.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatSession,
    EnhanceRequest,
    EnhanceResponse,
    IngestionResponse,
    PolicyRecord,
)
from src.storage.factory import get_storage

router = APIRouter(tags=["Sentinel Banking Intelligence"])

_agent = CopilotAgent()
_curator = CuratorPipeline()
_storage = get_storage()


@router.get("/health")
def health_check() -> Dict[str, Any]:
    """Return system status and storage backend health."""
    policies = _storage.get_all_policies()
    active_count = sum(1 for p in policies if p.active)
    return {
        "status": "HEALTHY",
        "storage_backend": type(_storage).__name__,
        "total_policies": len(policies),
        "active_policies": active_count,
        "superseded_policies": len(policies) - active_count,
    }


@router.post("/chat", response_model=ChatResponse)
def copilot_chat(request: ChatRequest) -> ChatResponse:
    """Submit a question to the policy-grounded Banking Copilot."""
    if not request.user_question.strip():
        raise HTTPException(status_code=400, detail="User question cannot be empty.")
    return _agent.answer_question(
        user_question=request.user_question,
        session_id=request.session_id,
        enhance_query=request.enhance_query,
    )


@router.post("/enhance", response_model=EnhanceResponse)
def enhance_query_endpoint(request: EnhanceRequest) -> EnhanceResponse:
    """Expand user shorthand banking acronyms and refine retrieval intent."""
    enhanced = enhance_banking_query(request.query)
    return EnhanceResponse(original_query=request.query, enhanced_query=enhanced)


@router.get("/sessions", response_model=List[ChatSession])
def list_sessions() -> List[ChatSession]:
    """Retrieve saved conversation sessions."""
    return _storage.list_sessions()


@router.get("/sessions/{session_id}", response_model=ChatSession)
def get_session(session_id: str) -> ChatSession:
    """Retrieve turn history for a single conversation session."""
    messages = _storage.get_session_messages(session_id, limit=50)
    if not messages:
        raise HTTPException(status_code=404, detail="Session not found.")
    return ChatSession(session_id=session_id, messages=messages)


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
def get_session_messages(session_id: str) -> List[ChatMessage]:
    """Retrieve turn messages for a session (Frontend compatibility)."""
    return _storage.get_session_messages(session_id, limit=50)


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str) -> Dict[str, str]:
    """Delete a conversation session."""
    _storage.delete_session(session_id)
    return {"status": "SUCCESS", "message": f"Session {session_id} deleted."}


@router.get("/policies", response_model=List[PolicyRecord])
def list_all_policies() -> List[PolicyRecord]:
    """List all indexed policies with their active/superseded status."""
    return _storage.get_all_policies()


@router.get("/graph")
def get_knowledge_graph() -> Dict[str, Any]:
    """Export graph nodes and edges for 2D/3D visualization."""
    return _storage.get_graph_data()


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...)) -> IngestionResponse:
    """Upload and ingest a new banking policy (PDF or PNG) into the knowledge graph."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing.")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".pdf", ".png", ".jpg", ".jpeg"):
        raise HTTPException(status_code=400, detail="Only PDF and PNG/JPG files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        # Ingest using curator
        result = _curator.ingest_file(tmp_path)
        # Rename result to match original filename
        result.document_name = file.filename
        return result
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@router.post("/upload", response_model=IngestionResponse)
async def upload_document(file: UploadFile = File(...)) -> IngestionResponse:
    """Upload alias for frontend compatibility."""
    return await ingest_document(file)
