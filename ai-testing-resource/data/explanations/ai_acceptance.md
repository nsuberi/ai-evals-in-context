# AI Acceptance Testing

AI Acceptance tests define the minimum acceptable behavior for AI features. Unlike traditional acceptance tests that verify "does the feature work?", AI acceptance tests verify "is the AI behaving within acceptable bounds?"

## What Makes AI Acceptance Different

Traditional acceptance testing has clear pass/fail criteria. AI systems introduce uncertainty:

| Traditional | AI |
|-------------|-----|
| Login succeeds or fails | Response may be partially correct |
| Price displays correctly | Price accuracy may vary |
| Form validates input | Validation quality depends on input |

## Key Concepts

### Grounding
AI responses must be traceable to source material. A grounded response:
- Cites specific documents
- Doesn't fabricate facts
- Stays within the knowledge domain

### Human-in-the-Loop
SMEs (Subject Matter Experts) define what "good" looks like:
- They validate initial quality criteria
- They review edge cases
- They approve threshold adjustments

### Statistical Thresholds
Unlike binary pass/fail:
```python
# Traditional acceptance
assert response.status_code == 200  # Binary: pass or fail

# AI acceptance
assert grounding_score >= 0.85  # Threshold: acceptable or not
```

## Relationship to AI Evals

AI Acceptance tests and AI Evals serve different purposes:

**Acceptance Tests** (these tests):
- Define hard requirements
- Answer: "Does it meet minimum standards?"
- Example: "Response must cite sources"

**AI Evals**:
- Measure quality distribution
- Answer: "How good is it across many cases?"
- Example: "85% of responses score 4+ on accuracy"

Think of it this way:
- **Acceptance**: Guardrails (must not cross)
- **Evals**: Quality measurement (continuous improvement)

## When to Use AI Acceptance Tests

Use AI acceptance tests for:
- Safety-critical requirements (no hallucinated medical advice)
- Legal/compliance requirements (accurate pricing, policies)
- Core product promises (responses must be grounded)

Use AI evals for:
- Measuring improvement over time
- Comparing model versions
- Understanding quality distribution
