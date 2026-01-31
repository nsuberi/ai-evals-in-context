"""
E2E Test: Version Comparison

Tests that different versions produce different behaviors
as documented in the educational material.
"""
import pytest
import os
from app.ai_service import ask_v1, ask_v2, ask_v3


# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)


class TestVersionComparison:
    """Test suite for version comparison"""

    @pytest.fixture(autouse=True)
    def setup(self, knowledge_base):
        """Ensure knowledge base is initialized"""
        pass

    def test_v1_is_verbose(self):
        """V1 should produce verbose responses (known issue)"""
        result = ask_v1("What is your return policy?")
        word_count = len(result['text'].split())

        # V1 should be verbose (>150 words typically)
        # This documents the expected failure mode
        assert word_count > 100, f"V1 should be verbose but was only {word_count} words"

    def test_v2_is_concise(self):
        """V2 should produce concise responses"""
        result = ask_v2("What is your return policy?")
        word_count = len(result['text'].split())

        # V2 should be around 80 words
        assert word_count < 150, f"V2 should be concise but was {word_count} words"

    def test_v3_has_sources(self):
        """V3 should include sources from RAG"""
        result = ask_v3("What is your return policy?")

        assert len(result['sources']) > 0, "V3 should cite sources"

    def test_v1_and_v2_have_no_sources(self):
        """V1 and V2 should not have sources"""
        result_v1 = ask_v1("What is your return policy?")
        result_v2 = ask_v2("What is your return policy?")

        assert len(result_v1['sources']) == 0
        assert len(result_v2['sources']) == 0

    def test_v3_uses_more_prompt_tokens(self):
        """V3 should use more prompt tokens due to RAG context"""
        result_v2 = ask_v2("What is your return policy?")
        result_v3 = ask_v3("What is your return policy?")

        # V3 includes context, so should have more prompt tokens
        assert result_v3['metadata']['prompt_tokens'] > result_v2['metadata']['prompt_tokens']
