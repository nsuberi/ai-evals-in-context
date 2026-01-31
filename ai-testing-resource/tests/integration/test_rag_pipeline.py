"""
Integration Test: RAG Pipeline

Tests the full retrieval-augmented generation pipeline:
embedding -> query -> context building -> response generation.
"""
import pytest
import os
from app.rag import get_relevant_docs, generate_embedding
from app.ai_service import ask_v3


class TestRAGPipeline:
    """Test suite for RAG pipeline"""

    @pytest.fixture(autouse=True)
    def setup(self, knowledge_base):
        """Ensure knowledge base is initialized"""
        pass

    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
    def test_embedding_generation(self):
        """Embedding should be generated for query"""
        embedding = generate_embedding("What is the return policy?")

        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    def test_retrieval_returns_documents(self):
        """Retrieval should return relevant documents"""
        docs = get_relevant_docs("enterprise pricing")

        assert len(docs) > 0
        # Should include pricing document
        assert any('pricing' in doc['id'].lower() or 'pricing' in doc['title'].lower()
                   for doc in docs)

    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
    def test_context_included_in_response(self):
        """V3 response should be grounded in retrieved context"""
        result = ask_v3("How much does the Enterprise plan cost?")

        # Response should mention the actual price from knowledge base
        assert '$299' in result['text'] or '299' in result['text']

        # Should have sources
        assert len(result['sources']) > 0

    def test_retrieval_relevance(self):
        """Retrieved docs should be relevant to query"""
        docs = get_relevant_docs("shipping time delivery")

        # At least one doc should be about shipping
        shipping_docs = [d for d in docs if 'shipping' in d['content'].lower()]
        assert len(shipping_docs) > 0

    def test_retrieval_for_pricing(self):
        """Retrieved docs for pricing query should include pricing info"""
        docs = get_relevant_docs("how much does the starter plan cost")

        pricing_docs = [d for d in docs if 'pricing' in d['id'].lower() or '$49' in d['content']]
        assert len(pricing_docs) > 0

    def test_retrieval_for_products(self):
        """Retrieved docs for product query should include product specs"""
        docs = get_relevant_docs("Widget Pro X2 specifications")

        product_docs = [d for d in docs if 'product' in d['id'].lower() or 'X2' in d['content']]
        assert len(product_docs) > 0
