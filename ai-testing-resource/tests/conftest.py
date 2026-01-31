"""Pytest configuration and fixtures"""

import pytest
import os
import sys

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.rag import initialize_knowledge_base


@pytest.fixture(scope="session")
def app():
    """Create application for testing"""
    app = create_app(testing=True)
    return app


@pytest.fixture(scope="session")
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope="session")
def knowledge_base():
    """Initialize knowledge base for tests"""
    initialize_knowledge_base()
    yield
    # Cleanup if needed


@pytest.fixture
def sample_questions():
    """Sample questions for testing"""
    return [
        "What is your return policy?",
        "How much does the Enterprise plan cost?",
        "What are the specs of Widget Pro X2?",
        "How long does shipping take?",
    ]


@pytest.fixture
def mock_ai_response():
    """Mock AI response for deterministic tests"""
    return {
        'text': "This is a mock response for testing purposes.",
        'sources': [],
        'metadata': {
            'latency_ms': 100,
            'prompt_tokens': 50,
            'completion_tokens': 20,
            'total_tokens': 70
        }
    }
