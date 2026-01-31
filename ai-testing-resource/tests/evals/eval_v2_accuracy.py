"""
AI Evaluation: V2 Factual Accuracy

Evaluates hallucination issues in V2. Without RAG, V2 makes up
specific details like pricing that don't match actual company data.

Expected result: FAIL - V2 hallucinates specific facts.
"""
import pytest
import os
from app.ai_service import ask_v2

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


class TestV2AccuracyEval:
    """Evaluation suite for V2 factual accuracy"""

    def test_enterprise_pricing_accuracy(self):
        """Response should state correct Enterprise plan price"""
        result = ask_v2("How much does the Enterprise plan cost?")

        # Check if response contains correct price
        assert '299' in result['text'], \
            f"Expected $299/month but got: {result['text'][:200]}..."

    def test_return_policy_accuracy(self):
        """Response should state correct return window"""
        result = ask_v2("How long do I have to return a product?")

        # Check for correct return window
        assert '30' in result['text'] and 'day' in result['text'].lower(), \
            f"Expected 30-day return window but got: {result['text'][:200]}..."

    def test_shipping_cost_accuracy(self):
        """Response should state correct shipping cost"""
        result = ask_v2("How much does express shipping cost?")

        # Check for correct express shipping price
        assert '12.95' in result['text'] or '12' in result['text'], \
            f"Expected $12.95 but got: {result['text'][:200]}..."

    def test_product_price_accuracy(self):
        """Response should state correct product price"""
        result = ask_v2("What is the price of Widget Pro X2?")

        # Check for correct product price
        assert '129' in result['text'], \
            f"Expected $129.99 but got: {result['text'][:200]}..."

    def test_no_fabricated_details(self):
        """Response should not include fabricated specific details"""
        result = ask_v2("Tell me about your premium support add-on")

        # There is no "premium support add-on" - response should acknowledge uncertainty
        hedging_phrases = ["don't have", 'not sure', 'contact', 'support team', 'not available']
        has_hedging = any(phrase in result['text'].lower() for phrase in hedging_phrases)

        # If no hedging, the model might be making things up
        assert has_hedging, \
            f"Model may have fabricated details about non-existent feature: {result['text'][:200]}..."
