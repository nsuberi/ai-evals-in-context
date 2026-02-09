# Performance Tests

Performance tests verify that the system responds quickly and uses resources efficiently. For example, a performance test measures whether the chatbot returns a response within 10 seconds and uses fewer than 500 completion tokens. AI API calls are expensive and slow compared to traditional code, so performance issues directly impact user experience and operational costs.

## Relationship to AI
**AI features have unique performance characteristics.** Token usage drives cost, and the tradeoff between context size (RAG retrieval) and response latency requires careful measurement. Performance tests track latency, token efficiency, and cost per request across model versions to prevent regressions.
