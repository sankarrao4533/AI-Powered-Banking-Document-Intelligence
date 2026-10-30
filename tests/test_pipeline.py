"""Integration tests for the BankingIntelligencePipeline."""

import pytest
from backend.core.pipeline import BankingIntelligencePipeline


def test_pipeline_metrics():
    pipeline = BankingIntelligencePipeline()
    metrics = pipeline.get_pipeline_metrics()

    assert "total_policies" in metrics
    assert "active_policies" in metrics
    assert "superseded_policies" in metrics
    assert metrics["total_policies"] >= 10
    assert metrics["active_policies"] >= 8
    assert metrics["superseded_policies"] >= 1


def test_pipeline_list_active_policies():
    pipeline = BankingIntelligencePipeline()
    active_policies = pipeline.list_active_policies()

    assert len(active_policies) >= 8
    for p in active_policies:
        assert p.active is True


def test_pipeline_invalid_query_validation():
    pipeline = BankingIntelligencePipeline()
    resp = pipeline.process_query("??")

    assert resp.governance_status == "VALIDATION_FAILED"
    assert "Validation Error" in resp.response
    assert len(resp.citations) == 0


def test_pipeline_process_valid_query():
    pipeline = BankingIntelligencePipeline()
    resp = pipeline.process_query("What is the lounge access policy for 2026?", enhance=True)

    assert resp.session_id is not None
    assert len(resp.response) > 0
    assert resp.governance_status in ("VERIFIED_ACTIVE", "FALLBACK_NO_ACTIVE_POLICY")
