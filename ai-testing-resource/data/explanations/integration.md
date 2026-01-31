# Integration Tests

Integration tests verify that different components work together correctly. They test the interactions between modules, services, and external systems.

## What We Test
- Chroma vector store connection and queries
- AI service integration with OpenAI API
- RAG pipeline (embedding → retrieval → context building)

## Why They Matter
Even if individual components work perfectly, they might fail when combined. Integration tests catch these "interface" bugs.

## Relationship to AI
**These test the infrastructure that powers your AI features.**

Integration tests verify:
- Vector database connections work
- Embeddings are generated correctly
- Retrieved documents have the expected structure
- API calls return valid responses

```python
# Integration test: RAG pipeline
def test_retrieval_returns_documents():
    docs = get_relevant_docs("return policy")

    assert len(docs) > 0
    assert any('return' in doc['content'].lower() for doc in docs)
```

## Key Difference from Unit Tests
Unit tests mock external dependencies. Integration tests use real connections to verify the actual integration works.
