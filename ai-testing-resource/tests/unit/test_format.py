"""
Unit Test: Response Formatting

Tests the format_response() utility that structures AI output
for consistent display.
"""
import pytest
from app.utils import format_response


class TestFormatResponse:
    """Test suite for response formatting"""

    def test_basic_format(self):
        """Basic response should have required fields"""
        result = format_response("Hello")

        assert 'text' in result
        assert 'sources' in result
        assert 'metadata' in result
        assert result['text'] == "Hello"

    def test_strips_whitespace(self):
        """Response text should be stripped"""
        result = format_response("  Hello world  ")
        assert result['text'] == "Hello world"

    def test_includes_sources(self):
        """Sources should be included when provided"""
        sources = [{'id': 'doc1', 'title': 'Test Doc'}]
        result = format_response("Hello", sources=sources)

        assert result['sources'] == sources

    def test_includes_metadata(self):
        """Metadata should be included"""
        result = format_response(
            "Hello",
            latency_ms=150,
            tokens={'prompt': 50, 'completion': 25}
        )

        assert result['metadata']['latency_ms'] == 150
        assert result['metadata']['prompt_tokens'] == 50
        assert result['metadata']['completion_tokens'] == 25
        assert result['metadata']['total_tokens'] == 75

    def test_default_values(self):
        """Missing values should have sensible defaults"""
        result = format_response("Hello")

        assert result['sources'] == []
        assert result['metadata']['latency_ms'] == 0
        assert result['metadata']['prompt_tokens'] == 0
        assert result['metadata']['completion_tokens'] == 0
        assert result['metadata']['total_tokens'] == 0

    def test_handles_multiline_text(self):
        """Multiline text should be preserved but stripped"""
        text = "  Line 1\nLine 2\nLine 3  "
        result = format_response(text)
        assert result['text'] == "Line 1\nLine 2\nLine 3"

    def test_empty_text(self):
        """Empty text should still format correctly"""
        result = format_response("")
        assert result['text'] == ""
        assert 'metadata' in result
