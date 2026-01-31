"""
Integration Test: AI Service

Tests the AI service integration with OpenAI API.
These tests require API credentials.
"""
import pytest
import os
from app.ai_service import ask, ask_v1, ask_v2, ask_v3


# Skip all tests if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)


class TestAIServiceIntegration:
    """Test suite for AI service integration"""

    @pytest.fixture(autouse=True)
    def setup(self, knowledge_base):
        """Ensure knowledge base is initialized"""
        pass

    def test_ask_returns_response(self):
        """ask() should return a properly formatted response"""
        result = ask("What is your return policy?", version='v3')

        assert 'text' in result
        assert 'metadata' in result
        assert len(result['text']) > 0

    def test_v1_produces_response(self):
        """V1 should produce a response"""
        result = ask_v1("What is your return policy?")

        assert 'text' in result
        assert len(result['text']) > 0
        assert result['metadata']['completion_tokens'] > 0

    def test_v2_produces_response(self):
        """V2 should produce a response"""
        result = ask_v2("What is your return policy?")

        assert 'text' in result
        assert len(result['text']) > 0
        assert result['metadata']['completion_tokens'] > 0

    def test_v3_produces_response_with_sources(self):
        """V3 should produce a response with sources"""
        result = ask_v3("What is your return policy?")

        assert 'text' in result
        assert 'sources' in result
        assert len(result['text']) > 0
        # V3 should have sources from RAG
        assert len(result['sources']) > 0

    def test_metadata_includes_latency(self):
        """Response metadata should include latency"""
        result = ask("Hello", version='v3')

        assert 'latency_ms' in result['metadata']
        assert result['metadata']['latency_ms'] > 0

    def test_metadata_includes_tokens(self):
        """Response metadata should include token counts"""
        result = ask("Hello", version='v3')

        assert 'prompt_tokens' in result['metadata']
        assert 'completion_tokens' in result['metadata']
        assert 'total_tokens' in result['metadata']
