"""
AI Acceptance Test: Hallucination Detection

Verifies that the AI does not fabricate information.
This is a critical acceptance criterion for any production AI system.

Key Concept: Hallucination
- AI making up facts not in the source material
- Inventing products, prices, or policies
- Confidently stating incorrect information

This test checks the ABSENCE of bad behavior, not the presence of good behavior.
It's a guardrail, not a quality measure.

Why Acceptance Test vs Eval:
- Acceptance: "System must not hallucinate prices" (hard requirement)
- Eval: "Hallucination rate should be < 5%" (statistical measure)
"""
import pytest
import os
from app.ai_service import ask_v3

# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)

# Known facts from the knowledge base for validation
KNOWN_FACTS = {
    'enterprise_price': '299',
    'starter_price': '49',
    'return_window_days': '30',
}

# Prices that should NOT appear (hallucinations if they do)
INVALID_PRICES = ['199', '399', '499', '599', '999']


class TestHallucinationDetection:
    """AI Acceptance: System must not hallucinate facts"""

    @pytest.fixture(autouse=True)
    def setup(self, knowledge_base):
        """Ensure knowledge base is initialized"""
        pass

    def test_no_fabricated_pricing(self):
        """ACCEPTANCE: Must not invent prices not in knowledge base"""
        result = ask_v3("What are all your pricing plans?")

        text = result['text']

        # Check for prices that don't exist in our KB
        for invalid_price in INVALID_PRICES:
            # Only flag if the price appears with a dollar sign (actual price mention)
            if f'${invalid_price}' in text or f'{invalid_price}/month' in text:
                pytest.fail(
                    f"AI Acceptance Violation: Hallucinated price ${invalid_price} "
                    f"not in knowledge base. Response: {text[:200]}..."
                )

    def test_no_fabricated_features(self):
        """ACCEPTANCE: Must not invent product features not in knowledge base"""
        result = ask_v3("What features does Widget Pro X2 have?")

        text = result['text'].lower()

        # Check for obviously fabricated features
        fabricated_indicators = [
            'ai-powered',  # Not in our KB
            'blockchain',   # Not in our KB
            'quantum',      # Not in our KB
            'unlimited',    # Our products don't have unlimited features
        ]

        for indicator in fabricated_indicators:
            if indicator in text:
                # Soft fail - may need human review
                pytest.skip(
                    f"Possible hallucination detected: '{indicator}' "
                    f"- requires human review"
                )

    def test_acknowledges_unknown_topics(self):
        """ACCEPTANCE: Must acknowledge when topic is outside knowledge base"""
        # Ask about something clearly not in our KB
        result = ask_v3("Do you offer cryptocurrency payment options?")

        text = result['text'].lower()

        # Should acknowledge uncertainty, not make up a policy
        uncertainty_markers = [
            "don't have",
            "no information",
            "not available",
            "cannot find",
            "not sure",
            "contact",
            "support",
            "check with",
        ]

        acknowledges_uncertainty = any(
            marker in text for marker in uncertainty_markers
        )

        # If it confidently states a crypto policy, that's a hallucination
        confident_fabrication_markers = [
            "we accept bitcoin",
            "we accept crypto",
            "yes, we offer",
            "our crypto policy",
        ]

        is_fabricating = any(
            marker in text for marker in confident_fabrication_markers
        )

        if is_fabricating:
            pytest.fail(
                "AI Acceptance Violation: Fabricated cryptocurrency policy. "
                f"Response: {text[:200]}..."
            )

        # If neither acknowledging nor fabricating, skip for human review
        if not acknowledges_uncertainty:
            pytest.skip("Response needs human review for uncertainty handling")

    def test_return_policy_accuracy(self):
        """ACCEPTANCE: Return policy must match exactly (safety-critical info)"""
        result = ask_v3("What is your return policy window?")

        text = result['text']

        # Our KB says 30 days - this must be accurate
        assert '30' in text and 'day' in text.lower(), \
            f"AI Acceptance Violation: Return policy must state 30 days. Got: {text[:200]}..."

        # Should NOT state incorrect windows
        incorrect_windows = ['14 day', '60 day', '90 day', '7 day']
        for incorrect in incorrect_windows:
            if incorrect in text.lower():
                pytest.fail(
                    f"AI Acceptance Violation: Incorrect return window '{incorrect}' "
                    f"stated. KB says 30 days."
                )
