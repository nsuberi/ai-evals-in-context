# End-to-End (E2E) Tests

E2E tests verify complete user flows from start to finish. They simulate real user interactions with the entire system.

## What We Test
- User can load the demo page
- User can submit a question
- User can select different versions
- Response is displayed correctly

## Why They Matter
E2E tests catch issues that only appear in the full system context—CSS problems, JavaScript errors, or workflow bugs that integration tests miss.

## Relationship to AI
**These test the complete experience of using your AI feature.**

E2E tests verify the user journey:
1. User opens the application
2. User types a question
3. User selects an AI version
4. User submits the request
5. User sees a response with metadata

```python
def test_ask_flow(client):
    # Load the page
    response = client.get('/ask')
    assert response.status_code == 200

    # Submit a question
    response = client.post('/ask', json={
        'question': 'What is your return policy?',
        'version': 'v3'
    })

    data = response.get_json()
    assert 'text' in data
    assert 'metadata' in data
```

## When to Use E2E Tests
E2E tests are slower and more brittle than unit tests. Use them sparingly for critical user paths, not for every feature.
