"""Unit tests for input and file validators."""

import pytest
from backend.utils.validators import (
    sanitize_input_text,
    validate_query,
    validate_session_id,
    validate_uploaded_file,
)


def test_validate_query_valid():
    is_valid, msg = validate_query("What is the lounge access limit for 2026?")
    assert is_valid is True
    assert msg == ""


def test_validate_query_empty_or_none():
    is_valid, msg = validate_query("")
    assert is_valid is False
    assert "short" in msg.lower()

    is_valid, msg = validate_query(None)
    assert is_valid is False
    assert "null" in msg.lower()


def test_validate_query_too_short():
    is_valid, msg = validate_query("ab")
    assert is_valid is False
    assert "too short" in msg.lower()


def test_validate_query_non_alphanumeric():
    is_valid, msg = validate_query("???!!!@@@")
    assert is_valid is False
    assert "alphanumeric" in msg.lower()


def test_validate_uploaded_file_valid_pdf():
    is_valid, msg = validate_uploaded_file("policy.pdf", 1024 * 50)
    assert is_valid is True
    assert msg == ""


def test_validate_uploaded_file_valid_png():
    is_valid, msg = validate_uploaded_file("rate_card.png", 1024 * 100)
    assert is_valid is True
    assert msg == ""


def test_validate_uploaded_file_disallowed_extension():
    is_valid, msg = validate_uploaded_file("malicious.exe", 1024 * 50)
    assert is_valid is False
    assert "unsupported file type" in msg.lower()


def test_validate_uploaded_file_zero_bytes():
    is_valid, msg = validate_uploaded_file("empty.pdf", 0)
    assert is_valid is False
    assert "empty" in msg.lower()


def test_validate_uploaded_file_oversized():
    is_valid, msg = validate_uploaded_file("huge.pdf", 30 * 1024 * 1024)
    assert is_valid is False
    assert "exceeds" in msg.lower()


def test_validate_session_id():
    assert validate_session_id("b87ecad6-87c2-491c-99fb-867c4e51be81") is True
    assert validate_session_id("session_12345") is True
    assert validate_session_id("") is False
    assert validate_session_id(None) is False
    assert validate_session_id("ab") is False  # too short (<4)


def test_sanitize_input_text():
    raw = "What is the LC limit?\x00\x08"
    sanitized = sanitize_input_text(raw)
    assert "\x00" not in sanitized
    assert "\x08" not in sanitized
    assert "What is the LC limit?" in sanitized
