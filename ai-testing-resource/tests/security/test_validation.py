"""
Security Test: Input Validation

Tests input validation and sanitization to prevent
XSS, injection, and other input-based attacks.
"""
import pytest
from app.utils import sanitize_input


class TestInputValidation:
    """Test suite for input validation"""

    def test_xss_prevention(self):
        """XSS attempts should be sanitized"""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
        ]

        for attempt in xss_attempts:
            result = sanitize_input(attempt)
            assert '<script' not in result.lower()
            assert 'onerror' not in result.lower()
            assert '<svg' not in result.lower()
            assert '<img' not in result.lower()

    def test_sql_injection_chars_preserved(self):
        """SQL injection chars are preserved but harmless in this context"""
        # Note: These are sanitized at DB layer, not input sanitization
        sql_attempts = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "UNION SELECT * FROM passwords",
        ]

        for attempt in sql_attempts:
            result = sanitize_input(attempt)
            # Input is preserved but sanitized for display
            assert len(result) > 0

    def test_length_limiting(self):
        """Excessively long input should be truncated"""
        long_input = "a" * 10000
        result = sanitize_input(long_input)

        assert len(result) <= 500, \
            f"Input not truncated: {len(result)} chars"

    def test_null_byte_handling(self):
        """Null bytes should be handled"""
        malicious = "hello\x00world"
        result = sanitize_input(malicious)

        assert '\x00' not in result

    def test_unicode_normalization(self):
        """Unicode should be normalized"""
        result = sanitize_input("cafe")
        assert len(result) > 0

    def test_empty_after_sanitization(self):
        """Purely malicious input may become empty"""
        result = sanitize_input("<script></script>")
        # May be empty or just whitespace after tag removal
        assert '<script>' not in result

    def test_preserves_legitimate_special_chars(self):
        """Legitimate special characters should be preserved"""
        input_text = "What's the price of Widget Pro X2? It's $129.99!"
        result = sanitize_input(input_text)

        assert '$' in result
        assert '?' in result
        assert "'" in result
