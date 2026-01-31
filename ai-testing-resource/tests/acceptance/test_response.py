"""
Acceptance Test: Response Quality

Tests that responses meet basic quality requirements
regardless of AI version.
"""
import pytest
import os
from app.ai_service import ask


# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)


class TestResponseQuality:
    """Test suite for response quality requirements"""

    @pytest.fixture(autouse=True)
    def setup(self, knowledge_base):
        """Ensure knowledge base is initialized"""
        pass

    def test_response_is_not_empty(self):
        """Response should not be empty"""
        result = ask("What is your return policy?", version='v3')

        assert len(result['text']) > 0

    def test_response_is_professional(self):
        """Response should not contain inappropriate content"""
        result = ask("What is your return policy?", version='v3')

        inappropriate_words = ['damn', 'hell', 'stupid', 'idiot']
        text_lower = result['text'].lower()

        for word in inappropriate_words:
            assert word not in text_lower

    def test_response_is_in_english(self):
        """Response should be in English"""
        result = ask("What is your return policy?", version='v3')

        # Check for common English words
        english_indicators = ['the', 'is', 'a', 'to', 'and', 'or', 'for', 'you', 'your', 'our']
        text_lower = result['text'].lower()

        matches = sum(1 for word in english_indicators if word in text_lower)
        assert matches >= 3, "Response should be in English"

    def test_response_addresses_question(self):
        """Response should address the question topic"""
        result = ask("What is your return policy?", version='v3')
        text_lower = result['text'].lower()

        # Should mention return-related terms
        return_terms = ['return', 'refund', 'policy', 'day', 'item']
        matches = sum(1 for term in return_terms if term in text_lower)

        assert matches >= 2, "Response should address return policy question"

    def test_response_includes_metadata(self):
        """Response should include metadata for transparency"""
        result = ask("Hello", version='v3')

        assert 'metadata' in result
        assert 'latency_ms' in result['metadata']
        assert 'total_tokens' in result['metadata']
