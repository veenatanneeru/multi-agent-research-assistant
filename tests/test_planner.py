"""Tests for the Planner agent's response-parsing logic.

These tests cover `_parse_sub_questions` only -- the pure-logic part of
the Planner that needs no LLM call, no network, and no API keys. They
run instantly and reliably anywhere, which is exactly why this is the
right piece to unit test (the LLM call itself is better covered by
manual/integration testing since its output isn't deterministic).
"""
from app.agents.planner import _parse_sub_questions


def test_parses_clean_json_array():
    raw = '["What is X?", "How does X work?", "What are risks of X?"]'
    result = _parse_sub_questions(raw, fallback_query="fallback")

    assert result == ["What is X?", "How does X work?", "What are risks of X?"]


def test_strips_markdown_code_fences():
    raw = '```json\n["What is X?", "How does X work?"]\n```'
    result = _parse_sub_questions(raw, fallback_query="fallback")

    assert result == ["What is X?", "How does X work?"]


def test_strips_plain_code_fences_without_json_label():
    raw = '```\n["What is X?"]\n```'
    result = _parse_sub_questions(raw, fallback_query="fallback")

    assert result == ["What is X?"]


def test_falls_back_on_invalid_json():
    raw = "This is not JSON at all, just a sentence."
    result = _parse_sub_questions(raw, fallback_query="original question")

    assert result == ["original question"]


def test_falls_back_on_json_that_is_not_a_string_list():
    # A JSON object instead of an array of strings should not be accepted.
    raw = '{"question": "What is X?"}'
    result = _parse_sub_questions(raw, fallback_query="original question")

    assert result == ["original question"]


def test_falls_back_on_empty_array():
    raw = "[]"
    result = _parse_sub_questions(raw, fallback_query="original question")

    assert result == ["original question"]


def test_strips_whitespace_and_drops_empty_strings():
    raw = '["  What is X?  ", "", "   ", "How does X work?"]'
    result = _parse_sub_questions(raw, fallback_query="fallback")

    assert result == ["What is X?", "How does X work?"]
