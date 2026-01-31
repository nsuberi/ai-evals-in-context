"""
AI Evaluation: V3 Knowledge Grounding

Evaluates V3's ability to provide accurate, grounded responses
using the RAG pipeline with Chroma.

Expected result: PASS - V3 should provide accurate, sourced responses.
"""
import pytest
import os
from app.ai_service import ask_v3

# Ground truth from knowledge base
GROUND_TRUTH = {
    'enterprise_price': '$299/month',
    'starter_price': '$49/month',
    'return_window': '30 days',
    'express_shipping': '$12.95',
    'widget_x2_price': '$129.99',
}

# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)


class TestV3GroundingEval:
    """Evaluation suite for V3 knowledge grounding"""

    @pytest.fixture(autouse=True)
    def setup(self, knowledge_base):
        """Ensure knowledge base is initialized"""
        pass

    def test_enterprise_pricing_grounded(self):
        """Response should cite correct Enterprise plan price from docs"""
        result = ask_v3("How much does the Enterprise plan cost?")

        # Should mention correct price
        assert '299' in result['text'], \
            f"Expected $299/month but got: {result['text'][:200]}..."

        # Should have sources
        assert len(result['sources']) > 0, "Response should cite sources"

    def test_return_policy_grounded(self):
        """Response should cite correct return window from docs"""
        result = ask_v3("What is your return policy?")

        assert '30' in result['text'] and 'day' in result['text'].lower(), \
            f"Expected 30-day mention but got: {result['text'][:200]}..."

        assert len(result['sources']) > 0, "Response should cite sources"

    def test_product_specs_grounded(self):
        """Response should cite correct product specs from docs"""
        result = ask_v3("What are the specs of Widget Pro X2?")

        # Check for actual specs from knowledge base
        assert any(spec in result['text'] for spec in ['5"', 'IP67', '3500mAh', '129']), \
            f"Expected product specs but got: {result['text'][:200]}..."

        assert len(result['sources']) > 0, "Response should cite sources"

    def test_unknown_topic_acknowledged(self):
        """Unknown topics should be acknowledged, not fabricated"""
        result = ask_v3("What is your cryptocurrency payment policy?")

        # Should acknowledge lack of information (no crypto docs in KB)
        uncertain_phrases = ["don't have", 'no information', 'contact', 'support']
        has_uncertainty = any(phrase in result['text'].lower() for phrase in uncertain_phrases)

        assert has_uncertainty, \
            f"Should acknowledge unknown topic but got: {result['text'][:200]}..."

    def test_sources_are_relevant(self):
        """Cited sources should be relevant to the question"""
        result = ask_v3("How much does shipping cost?")

        # Sources should include shipping document
        source_ids = [s['id'] for s in result['sources']]
        source_titles = [s['title'].lower() for s in result['sources']]

        has_shipping_source = any(
            'shipping' in sid or 'shipping' in title
            for sid, title in zip(source_ids, source_titles)
        )

        assert has_shipping_source, \
            f"Expected shipping source but got: {result['sources']}"

    def test_response_length_appropriate(self):
        """V3 should still maintain appropriate response length"""
        result = ask_v3("What is your return policy?")
        word_count = len(result['text'].split())

        # Should be concise (~80 words, allow 60-120)
        assert 40 <= word_count <= 150, \
            f"Response was {word_count} words (expected 60-120)"
