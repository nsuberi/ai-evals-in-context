"""
Integration Test: Chroma Vector Store

Tests the Chroma database integration for storing and retrieving
knowledge base documents. Requires Chroma to be running.
"""
import pytest
from app.rag import get_relevant_docs, initialize_knowledge_base, get_collection


class TestChromaIntegration:
    """Test suite for Chroma vector store"""

    @pytest.fixture(autouse=True)
    def setup(self, knowledge_base):
        """Ensure knowledge base is initialized"""
        pass

    def test_collection_exists(self):
        """Collection should exist after initialization"""
        collection = get_collection()
        assert collection is not None
        assert collection.count() > 0

    def test_retrieves_relevant_docs(self):
        """Query should return relevant documents"""
        docs = get_relevant_docs("return policy", n_results=3)

        assert len(docs) > 0
        assert any('return' in doc['content'].lower() for doc in docs)

    def test_returns_expected_structure(self):
        """Retrieved docs should have required fields"""
        docs = get_relevant_docs("pricing", n_results=1)

        assert len(docs) == 1
        doc = docs[0]

        assert 'id' in doc
        assert 'title' in doc
        assert 'content' in doc
        assert 'distance' in doc

    def test_respects_n_results(self):
        """Should return requested number of results"""
        docs = get_relevant_docs("widgets", n_results=2)
        assert len(docs) <= 2

    def test_handles_no_matches(self):
        """Query with no matches should return empty list or distant results"""
        docs = get_relevant_docs("xyzzy123nonsense", n_results=3)
        # May still return results with high distance
        assert isinstance(docs, list)
