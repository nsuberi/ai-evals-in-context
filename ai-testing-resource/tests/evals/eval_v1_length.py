"""
AI Evaluation: V1 Response Length

Evaluates the verbose prompt issue in V1. These tests demonstrate
how evals identify specification mismatches.

Expected result: FAIL - V1 produces responses that are too long.
"""
import pytest
import os
from app.ai_service import ask_v1
from app.utils import count_tokens

# Target: ~80 words, Acceptable range: 60-100 words
TARGET_WORD_COUNT = 80
ACCEPTABLE_MIN = 60
ACCEPTABLE_MAX = 100

# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)


class TestV1LengthEval:
    """Evaluation suite for V1 response length"""

    @pytest.fixture
    def questions(self):
        return [
            "What is your return policy?",
            "How much does shipping cost?",
            "What are your business hours?",
        ]

    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())

    def test_return_policy_length(self):
        """Response to return policy should be ~80 words"""
        result = ask_v1("What is your return policy?")
        word_count = self.count_words(result['text'])

        # This should FAIL - V1 produces 300+ word responses
        assert ACCEPTABLE_MIN <= word_count <= ACCEPTABLE_MAX, \
            f"Response was {word_count} words (expected {ACCEPTABLE_MIN}-{ACCEPTABLE_MAX})"

    def test_shipping_cost_length(self):
        """Response to shipping cost should be ~80 words"""
        result = ask_v1("How much does shipping cost?")
        word_count = self.count_words(result['text'])

        assert ACCEPTABLE_MIN <= word_count <= ACCEPTABLE_MAX, \
            f"Response was {word_count} words (expected {ACCEPTABLE_MIN}-{ACCEPTABLE_MAX})"

    def test_average_length_across_questions(self, questions):
        """Average response length should be ~80 words"""
        total_words = 0

        for question in questions:
            result = ask_v1(question)
            total_words += self.count_words(result['text'])

        avg_words = total_words / len(questions)

        assert ACCEPTABLE_MIN <= avg_words <= ACCEPTABLE_MAX, \
            f"Average was {avg_words:.0f} words (expected {ACCEPTABLE_MIN}-{ACCEPTABLE_MAX})"
