"""
Unit Test: Input Sanitization

Tests the sanitize_input() utility function that cleans user input
before processing. These tests are deterministic - no AI involved.
"""
import pytest
from app.utils import sanitize_input


class TestSanitizeInput:
    """Test suite for input sanitization"""

    def test_strips_whitespace(self):
        """Leading/trailing whitespace should be removed"""
        assert sanitize_input("  hello world  ") == "hello world"

    def test_removes_html_tags(self):
        """HTML tags should be stripped for security"""
        assert sanitize_input("<script>alert('xss')</script>hello") == "alert('xss')hello"
        assert sanitize_input("<b>bold</b>") == "bold"

    def test_limits_length(self):
        """Input should be truncated to 500 characters"""
        long_input = "a" * 1000
        result = sanitize_input(long_input)
        assert len(result) == 500

    def test_normalizes_whitespace(self):
        """Multiple spaces should become single space"""
        assert sanitize_input("hello    world") == "hello world"
        assert sanitize_input("hello\n\nworld") == "hello world"

    def test_handles_empty_input(self):
        """Empty or None input should return empty string"""
        assert sanitize_input("") == ""
        assert sanitize_input(None) == ""

    def test_preserves_valid_input(self):
        """Normal input should pass through unchanged"""
        assert sanitize_input("What is your return policy?") == "What is your return policy?"

    def test_handles_mixed_malicious_input(self):
        """Combination of issues should all be handled"""
        malicious = "  <script>alert('xss')</script>  What   is   your   return   policy?  "
        result = sanitize_input(malicious)
        assert "<script>" not in result
        assert "  " not in result  # No double spaces
        assert result.startswith("alert")  # Stripped leading whitespace
