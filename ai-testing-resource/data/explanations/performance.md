# Performance Tests

Performance tests verify that the system responds quickly and uses resources efficiently. For AI systems, this includes latency and token usage.

## What We Test
- Response latency (time to first response)
- Token efficiency (cost per request)
- Consistency (variance across requests)
- Throughput (requests per second)

## Why They Matter
AI API calls are expensive and slow compared to traditional code. Performance issues directly impact user experience and operational costs.

## Relationship to AI
**AI features have unique performance characteristics.**

### Latency Testing
```python
def test_latency_acceptable():
    start = time.time()
    result = ask_v3("What is your return policy?")
    latency_ms = (time.time() - start) * 1000

    assert latency_ms < 10000  # 10 seconds max
```

### Token Efficiency
```python
def test_token_efficiency():
    result = ask_v3("What is your return policy?")

    # Completion tokens should be reasonable
    assert result['metadata']['completion_tokens'] < 500

    # V3 has more prompt tokens due to RAG context
    assert result['metadata']['prompt_tokens'] > 100
```

## Key Metrics

| Metric | V1 | V2 | V3 |
|--------|----|----|-----|
| Avg Latency | 2.5s | 1.2s | 1.8s |
| Completion Tokens | 300+ | ~80 | ~80 |
| Prompt Tokens | ~90 | ~70 | ~450 |

## Trade-offs

- **V3 uses more prompt tokens** because it includes RAG context
- **V1 uses more completion tokens** because it produces verbose responses
- **V3 has slightly higher latency** due to retrieval step

## Cost Implications

Token usage directly affects cost. For Claude Sonnet:
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

V1's verbose responses cost more per request, but V3's larger prompts also add up. Monitor both.
