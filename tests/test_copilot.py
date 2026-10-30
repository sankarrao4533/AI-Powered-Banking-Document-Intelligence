"""Copilot agent responses and API endpoint integration tests."""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.copilot.agent import CopilotAgent


client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["active_policies"] >= 10


def test_api_list_policies():
    res = client.get("/api/policies")
    assert res.status_code == 200
    policies = res.json()
    assert len(policies) >= 12
    # Verify supersession state
    p2026 = next((p for p in policies if p["name"] == "Credit_Card_Lounge_Access_2026.pdf"), None)
    p2024 = next((p for p in policies if p["name"] == "Credit_Card_Lounge_Access_2024.pdf"), None)

    assert p2026 is not None and p2026["active"] is True
    assert p2024 is not None and p2024["active"] is False


def test_api_chat_lounge_access():
    res = client.post(
        "/api/chat",
        json={
            "user_question": "What is the lounge access limit for Signature cards in 2026?",
            "enhance_query": True,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert len(data["citations"]) > 0
    # Must cite 2026 policy
    assert data["citations"][0]["document_name"] == "Credit_Card_Lounge_Access_2026.pdf"


def test_api_chat_msme_lc_limit():
    agent = CopilotAgent()
    resp = agent.answer_question("What is the maximum unsecured Letter of Credit (LC) limit for MSMEs?")
    assert resp.governance_status == "VERIFIED_ACTIVE"
    assert "50 Lakhs" in resp.response or "50" in resp.response
