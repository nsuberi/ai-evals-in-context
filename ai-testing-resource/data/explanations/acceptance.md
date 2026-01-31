# Acceptance Tests

Acceptance tests verify that the system meets business requirements from the user's perspective. They answer: "Does this feature do what the customer needs?"

## What We Test
- User can access the demo page
- Response is not empty
- Response is professional and appropriate
- Response addresses the question topic

## Why They Matter
Acceptance tests ensure you're building the right thing, not just building it correctly. They translate business requirements into verifiable tests.

## Relationship to AI
**For traditional software, acceptance tests verify requirements. For AI features, this is where evals come in.**

Traditional acceptance test:
```python
def test_user_can_ask_question():
    response = client.post('/ask', json={'question': 'Hello'})
    assert response.status_code == 200
    assert len(response.json()['text']) > 0
```

This passes if *any* response is returned. But for AI, we need more:
- Is the response *accurate*?
- Is it the *right length*?
- Is it *grounded in facts*?

These are AI evals—acceptance tests for AI behavior.

## The Gap
Traditional acceptance tests check *that* something works.
AI evals check *how well* something works.

This is why AI evals are often statistical: "80% of responses should be under 100 words" rather than "this response is under 100 words."
