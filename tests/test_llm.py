"""Tests for the LLM module - JSON parsing, sanitization, concept counting."""

import pytest

from learnlock.llm import (
    _calc_concept_count,
    _extract_json_from_response,
    _normalize_excerpt,
    _quote_appears_in_source,
    parse_json_response,
    sanitize_for_prompt,
)


class TestParseJsonResponse:
    def test_valid_json_array(self):
        result = parse_json_response('[{"a": 1}, {"a": 2}]')
        assert isinstance(result, list)
        assert len(result) == 2

    def test_valid_json_object(self):
        result = parse_json_response('{"score": 3}')
        assert result["score"] == 3

    def test_code_block(self):
        result = parse_json_response('```json\n[{"a": 1}]\n```')
        assert isinstance(result, list)

    def test_trailing_comma_fixed(self):
        result = parse_json_response('{"a": 1, "b": 2,}')
        assert result["a"] == 1

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Could not parse JSON"):
            parse_json_response("this is not json at all")

    def test_extracts_from_surrounding_text(self):
        result = parse_json_response('Here is the result: {"score": 5} hope that helps')
        assert result["score"] == 5

    def test_individual_objects_fallback(self):
        raw = 'blah {"a":1} blah {"b":2} blah'
        result = parse_json_response(raw)
        assert isinstance(result, list)
        assert len(result) == 2


class TestExtractJsonFromResponse:
    def test_bare_json(self):
        assert _extract_json_from_response('{"a":1}') == '{"a":1}'

    def test_code_block_with_lang(self):
        raw = "```json\n{}\n```"
        assert _extract_json_from_response(raw) == "{}"

    def test_code_block_without_lang(self):
        raw = "```\n[1,2]\n```"
        assert _extract_json_from_response(raw) == "[1,2]"


class TestSanitizeForPrompt:
    def test_removes_null_bytes(self):
        assert sanitize_for_prompt("hello\x00world") == "helloworld"

    def test_removes_control_chars(self):
        assert sanitize_for_prompt("a\x01b\x02c") == "abc"

    def test_keeps_newlines_and_tabs(self):
        assert sanitize_for_prompt("a\nb\tc") == "a\nb\tc"

    def test_collapses_excessive_newlines(self):
        result = sanitize_for_prompt("a\n\n\n\n\nb")
        assert result == "a\n\nb"

    def test_truncation(self):
        result = sanitize_for_prompt("abcdefgh", max_length=5)
        assert result == "abcde"

    def test_no_truncation_by_default(self):
        long_text = "x" * 10000
        assert len(sanitize_for_prompt(long_text)) == 10000


class TestCalcConceptCount:
    def test_short_content(self):
        min_c, max_c = _calc_concept_count(500)
        assert min_c >= 5
        assert max_c >= min_c

    def test_long_content(self):
        min_c, max_c = _calc_concept_count(10000)
        assert max_c <= 20

    def test_empty_content(self):
        min_c, max_c = _calc_concept_count(0)
        assert min_c >= 5  # floor is 5
        assert max_c >= min_c


class TestQuoteAppearsInSource:
    def test_exact_match(self):
        assert _quote_appears_in_source("hello world", "hello world")

    def test_case_insensitive(self):
        assert _quote_appears_in_source("Hello World", "hello world")

    def test_whitespace_normalized(self):
        assert _quote_appears_in_source("hello   world", "hello world")

    def test_substring_match(self):
        assert _quote_appears_in_source("the quick brown fox", "quick brown")

    def test_no_match(self):
        assert not _quote_appears_in_source("hello world", "goodbye moon")

    def test_empty_quote(self):
        assert not _quote_appears_in_source("hello", "")


class TestNormalizeExcerpt:
    def test_collapses_whitespace(self):
        assert _normalize_excerpt("  a   b   c  ") == "a b c"

    def test_lowercases(self):
        assert _normalize_excerpt("HELLO") == "hello"
