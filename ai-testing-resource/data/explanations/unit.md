# Unit Tests

Unit tests verify that individual functions work correctly in isolation. They test the smallest testable parts of your application.

## What We Test
- Input sanitization (does it remove dangerous characters?)
- Token counting (does it return accurate counts?)
- Response formatting (does it structure data correctly?)

## Why They Matter
Unit tests catch bugs early and make refactoring safe. When a unit test fails, you know exactly which function broke.

## Relationship to AI
**These test the code *around* your AI—not the AI itself.**

Unit tests should be deterministic: given the same input, they always produce the same output. AI responses are inherently non-deterministic, so we don't unit test AI behavior.

Instead, we unit test:
- Input preprocessing before it reaches the AI
- Output formatting after the AI responds
- Helper utilities like token counting

```python
# This is a unit test ✓
def test_sanitize_input():
    assert sanitize_input("<script>") == ""

# This is NOT a unit test ✗
def test_ai_response():
    response = ask_ai("Hello")  # Non-deterministic!
    assert "Hello" in response
```
