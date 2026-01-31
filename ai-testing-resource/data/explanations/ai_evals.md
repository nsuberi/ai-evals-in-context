# AI Evaluations

AI Evals are **acceptance tests for AI behavior**. They verify that your AI produces outputs that meet your quality criteria.

## The Core Insight

Traditional acceptance tests ask: "Does the system do what the user needs?"

AI Evals ask the same question, but for AI-generated content:
- Is the response accurate?
- Is it the right length?
- Is it grounded in facts (not hallucinated)?
- Does it follow the specified format?

## Why They're Different

Unlike unit tests, evals often involve:
- **Statistical evaluation**: "80% of responses should be under 100 words"
- **Human judgment proxies**: Using LLMs to evaluate LLM outputs
- **Regression detection**: Did the new prompt make things worse?

## The Iterative Process

```
1. Deploy V1 → Collect traces
2. Annotate failures → "Responses too verbose"
3. Fix prompt → Deploy V2
4. Collect traces → Annotate
5. Find new issues → "Hallucinating facts"
6. Add RAG → Deploy V3
7. Verify improvement
```

## Relationship to Testing Pyramid

```
        /\
       /  \  ← AI Evals (acceptance for AI)
      /----\
     /      \ ← Traditional Acceptance
    /--------\
   /          \ ← E2E, Integration
  /------------\
 /              \ ← Unit Tests
```

AI Evals sit at the acceptance level because they verify user-facing quality. But unlike traditional acceptance tests, they require:
- More test cases (statistical significance)
- Tolerance for variation (not binary pass/fail)
- Continuous monitoring (AI behavior can drift)

## Types of Evals in This Project

### Length Evals (V1)
```python
def test_response_length():
    result = ask_v1("What is your return policy?")
    word_count = len(result['text'].split())
    assert 60 <= word_count <= 100  # Fails! V1 produces 300+ words
```

### Accuracy Evals (V2)
```python
def test_pricing_accuracy():
    result = ask_v2("How much is Enterprise plan?")
    assert '299' in result['text']  # Fails! V2 hallucinates prices
```

### Grounding Evals (V3)
```python
def test_response_is_grounded():
    result = ask_v3("What is your return policy?")
    assert len(result['sources']) > 0  # Passes! V3 cites sources
    assert '30' in result['text']  # Passes! Correct return window
```
