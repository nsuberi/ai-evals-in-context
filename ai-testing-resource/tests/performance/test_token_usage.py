"""
Performance Test: Token Efficiency

Tests that token usage is reasonable and within budget.
Important for cost management.
"""
import pytest
import os
from app.ai_service import ask_v1, ask_v2, ask_v3

# Token thresholds
MAX_PROMPT_TOKENS = 2000    # Maximum prompt tokens
MAX_COMPLETION_TOKENS = 500  # Maximum completion tokens
TARGET_COMPLETION_V1 = 400   # V1 expected (verbose)
TARGET_COMPLETION_V2_V3 = 150  # V2/V3 expected (concise)

# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)


class TestTokenUsage:
    """Test suite for token efficiency"""

    @pytest.fixture(autouse=True)
    def setup(self, knowledge_base):
        pass

    def test_v1_completion_tokens(self):
        """V1 completion tokens should be high (known issue)"""
        result = ask_v1("What is your return policy?")
        completion_tokens = result['metadata']['completion_tokens']

        # V1 is expected to use more tokens (verbose prompt)
        # This test documents the expected behavior
        assert completion_tokens > TARGET_COMPLETION_V2_V3, \
            f"V1 should be verbose but only used {completion_tokens} tokens"

    def test_v2_token_efficiency(self):
        """V2 should use fewer completion tokens"""
        result = ask_v2("What is your return policy?")
        completion_tokens = result['metadata']['completion_tokens']

        assert completion_tokens < MAX_COMPLETION_TOKENS, \
            f"V2 used {completion_tokens} tokens (max: {MAX_COMPLETION_TOKENS})"

    def test_v3_token_efficiency(self):
        """V3 should use reasonable completion tokens"""
        result = ask_v3("What is your return policy?")
        completion_tokens = result['metadata']['completion_tokens']

        assert completion_tokens < MAX_COMPLETION_TOKENS, \
            f"V3 used {completion_tokens} tokens (max: {MAX_COMPLETION_TOKENS})"

    def test_v3_prompt_tokens_reasonable(self):
        """V3 prompt tokens should account for RAG context"""
        result = ask_v3("What is your return policy?")
        prompt_tokens = result['metadata']['prompt_tokens']

        # V3 includes retrieved context, so prompt is larger
        assert prompt_tokens < MAX_PROMPT_TOKENS, \
            f"V3 prompt used {prompt_tokens} tokens (max: {MAX_PROMPT_TOKENS})"

        # But should be larger than base prompt
        assert prompt_tokens > 100, \
            "V3 prompt should include RAG context"

    def test_v2_vs_v3_prompt_tokens(self):
        """V3 should use more prompt tokens than V2 due to RAG"""
        result_v2 = ask_v2("What is your return policy?")
        result_v3 = ask_v3("What is your return policy?")

        v2_prompt = result_v2['metadata']['prompt_tokens']
        v3_prompt = result_v3['metadata']['prompt_tokens']

        assert v3_prompt > v2_prompt, \
            f"V3 ({v3_prompt}) should use more prompt tokens than V2 ({v2_prompt})"
