# Integration Tests

Integration tests verify that different components work together correctly. For example, an integration test confirms that the RAG pipeline can embed a query, retrieve relevant documents from the vector store, and assemble context for the AI model. Even if individual pieces work in isolation, they can fail at their boundaries.

## Relationship to AI
**These test the infrastructure that powers your AI features.** Integration tests verify that vector database connections work, embeddings are generated correctly, retrieved documents have the expected structure, and API calls return valid responses.
