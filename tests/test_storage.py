"""Test storage operations, graph traversal, and SQLite persistence."""

import pytest
from src.storage.factory import get_storage
from src.models.schemas import PolicyRecord


def test_storage_policy_lifecycle():
    storage = get_storage()
    all_p = storage.get_all_policies()
    assert len(all_p) >= 10

    # Verify categories exist
    graph_data = storage.get_graph_data()
    cat_nodes = [n for n in graph_data["nodes"] if n["type"] == "Category"]
    assert len(cat_nodes) == 5

    # Verify links
    belongs_to_links = [l for l in graph_data["links"] if l["relation"] == "BELONGS_TO"]
    assert len(belongs_to_links) >= 10


def test_session_message_persistence():
    storage = get_storage()
    test_sid = "test-session-123"

    storage.save_chat_message(session_id=test_sid, role="user", content="Hello test")
    storage.save_chat_message(session_id=test_sid, role="assistant", content="Response test")

    msgs = storage.get_session_messages(session_id=test_sid)
    assert len(msgs) == 2
    assert msgs[0].role == "user"
    assert msgs[1].content == "Response test"

    # Cleanup
    storage.delete_session(test_sid)
    msgs_after = storage.get_session_messages(session_id=test_sid)
    assert len(msgs_after) == 0
