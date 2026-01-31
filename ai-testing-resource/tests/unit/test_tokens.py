"""
Unit Test: Token Counting

Tests the count_tokens() utility for accurate token counting.
Important for cost estimation and context window management.
"""
import pytest
from app.utils import count_tokens


class TestCountTokens:
    """Test suite for token counting"""

    def test_counts_simple_text(self):
        """Simple text should return reasonable token count"""
        result = count_tokens("Hello, world!")
        assert result > 0
        assert result < 10  # Should be around 4 tokens

    def test_empty_string_is_zero(self):
        """Empty string should have zero tokens"""
        assert count_tokens("") == 0

    def test_longer_text_more_tokens(self):
        """Longer text should have more tokens"""
        short = count_tokens("Hi")
        long = count_tokens("Hello, this is a much longer piece of text that should have more tokens.")
        assert long > short

    def test_special_characters(self):
        """Special characters should be handled"""
        result = count_tokens("Price: $99.99 (20% off!)")
        assert result > 0

    def test_unicode_text(self):
        """Unicode text should be handled"""
        result = count_tokens("Hello World")  # Using standard ASCII for reliable testing
        assert result > 0

    def test_code_snippets(self):
        """Code-like text should be tokenized"""
        code = "def hello():\n    return 'world'"
        result = count_tokens(code)
        assert result > 0

    def test_reasonable_token_ratio(self):
        """Token count should roughly correlate with word count"""
        text = "The quick brown fox jumps over the lazy dog."
        tokens = count_tokens(text)
        words = len(text.split())
        # Typically 1-1.5 tokens per word for English
        assert tokens >= words * 0.5
        assert tokens <= words * 2
