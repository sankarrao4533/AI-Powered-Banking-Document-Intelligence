"""Abstract base interface for Sentinel Knowledge Graph and Vector Storage."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence

from src.models.schemas import ActivePolicy, ChatMessage, ChatSession, PolicyRecord


class BaseStorage(ABC):
    """Abstract interface supporting both Neo4j and Embedded storage backends."""

    @abstractmethod
    def initialize_ontology(self) -> None:
        """Reset or initialize root banking ontology categories."""
        pass

    @abstractmethod
    def save_policy(self, policy: PolicyRecord) -> None:
        """Insert or update a policy node and its relational edges."""
        pass

    @abstractmethod
    def supersede_policy(self, new_policy_name: str, old_policy_name: str) -> None:
        """Link new policy to old policy via SUPERSEDES edge and deactivate old policy."""
        pass

    @abstractmethod
    def query_active_policies(
        self,
        query_text: str,
        query_embedding: Sequence[float],
        top_k: int = 5,
    ) -> List[ActivePolicy]:
        """Hybrid search with governance firewall (active-only)."""
        pass

    @abstractmethod
    def get_all_policies(self) -> List[PolicyRecord]:
        """Return all policies with their active/superseded status."""
        pass

    @abstractmethod
    def get_policy(self, name: str) -> Optional[PolicyRecord]:
        """Lookup a policy by document name."""
        pass

    @abstractmethod
    def get_graph_data(self) -> Dict[str, Any]:
        """Return nodes and edges formatted for visualization."""
        pass

    @abstractmethod
    def save_chat_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: Optional[List[ActivePolicy]] = None,
    ) -> None:
        """Append a message turn to persistent session memory."""
        pass

    @abstractmethod
    def get_session_messages(self, session_id: str, limit: int = 20) -> List[ChatMessage]:
        """Retrieve recent conversation turns for a session."""
        pass

    @abstractmethod
    def list_sessions(self) -> List[ChatSession]:
        """List all active conversation sessions."""
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        """Delete a conversation session."""
        pass
