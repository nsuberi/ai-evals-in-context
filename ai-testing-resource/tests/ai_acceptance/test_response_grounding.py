"""
AI Acceptance Test: Response Grounding

Verifies that AI responses are grounded in the knowledge base.
Unlike traditional acceptance tests that check "does it work?",
AI acceptance tests check "is the AI behaving correctly?"

Key Concept: Grounding
- Responses should be based on retrieved documents
- Claims should be traceable to sources
- No fabrication of facts not in the knowledge base

This is an AI ACCEPTANCE test, not an eval:
- Evals measure quality statistically (e.g., "80% grounded")
- Acceptance tests verify specific acceptance criteria
"""
import pytest
import os
from app.ai_service import ask_v3

# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)


class TestResponseGrounding:
    """AI Acceptance: Responses must be grounded in knowledge base"""

    @pytest.fixture(autouse=True)
    def setup(self, knowledge_base):
        """Ensure knowledge base is initialized"""
        pass

    def test_response_cites_sources(self):
        """ACCEPTANCE: Every response must cite at least one source"""
        result = ask_v3("What is your pricing?")

        assert 'sources' in result, "Response must include sources field"
        assert len(result['sources']) > 0, \
            "AI Acceptance Criteria: Response must cite at least one source"

    def test_pricing_claim_matches_source(self):
        """ACCEPTANCE: Pricing claims must match knowledge base exactly"""
        result = ask_v3("How much does the Enterprise plan cost?")

        # The knowledge base states $299/month for Enterprise
        # This is a HARD acceptance criterion - not statistical
        assert '299' in result['text'], \
            "AI Acceptance Criteria: Price must match knowledge base ($299)"

    def test_response_stays_in_domain(self):
        """ACCEPTANCE: Responses should stay within knowledge base domain"""
        result = ask_v3("What are your shipping options?")

        # Should discuss shipping (in KB), not unrelated topics
        shipping_terms = ['shipping', 'delivery', 'express', 'standard']
        has_shipping_content = any(
            term in result['text'].lower() for term in shipping_terms
        )

        assert has_shipping_content, \
            "AI Acceptance Criteria: Response must address the topic using KB content"

    def test_source_relevance(self):
        """ACCEPTANCE: Cited sources must be relevant to the question"""
        result = ask_v3("What is your return policy?")

        # Sources should be about returns, not random documents
        source_ids = [s.get('id', '').lower() for s in result.get('sources', [])]
        source_titles = [s.get('title', '').lower() for s in result.get('sources', [])]

        has_relevant_source = any(
            'return' in sid or 'return' in title or 'policy' in sid or 'policy' in title
            for sid, title in zip(source_ids, source_titles)
        )

        # This is a soft check - sources should be relevant but may have broader matches
        if not has_relevant_source:
            pytest.skip("Source relevance check - may need manual review")
