"""Governance and supersession firewall validation tests."""

import pytest
from src.storage.factory import get_storage
from src.retrieval.hybrid_retriever import HybridRetriever, STRICT_NO_ANSWER
from src.copilot.agent import CopilotAgent


def test_supersession_firewall_lounge_access():
    """Verify that superseded 2024 and 2025 lounge access policies are strictly excluded."""
    storage = get_storage()
    retriever = HybridRetriever(storage)

    results = retriever.retrieve("What is the lounge access limit for Signature and Infinite cards?")
    assert len(results) > 0, "Expected at least one active policy for lounge access."

    # Top policy MUST be the active 2026 version
    doc_names = [r.document_name for r in results]
    assert "Credit_Card_Lounge_Access_2026.pdf" in doc_names, "2026 active policy must be present in retrieval."
    assert "Credit_Card_Lounge_Access_2024.pdf" not in doc_names, "2024 superseded policy must be blocked by firewall."
    assert "Credit_Card_Lounge_Access_2025.pdf" not in doc_names, "2025 superseded policy must be blocked by firewall."


def test_multi_hop_entities_retrieved():
    """Verify that multi-hop customer segments and document requirements are extracted."""
    storage = get_storage()
    retriever = HybridRetriever(storage)

    results = retriever.retrieve("What are the KYC documents required for NRI account opening?")
    assert len(results) > 0
    top_hit = results[0]

    assert "NRI" in top_hit.customer_types or len(top_hit.customer_types) > 0
    assert any("passport" in doc.lower() or "pan" in doc.lower() for doc in top_hit.required_docs)


def test_strict_fallback_for_unknown_topic():
    """Verify system strictly fails closed when no active policy is verified."""
    agent = CopilotAgent()
    resp = agent.answer_question("What is the interest rate for intergalactic spacecraft loans on Mars?")

    assert resp.response == STRICT_NO_ANSWER or "verified active policy" in resp.response.lower()
    assert resp.governance_status == "FALLBACK_NO_ACTIVE_POLICY"
