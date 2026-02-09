# Testing Strategy &mdash; Where AI Evals Fit

## The Test Pyramid with AI Evals

```
                +-------------------------+
                |    AI ACCEPTANCE        |  <- AI Evals live here
                |    - Grounding          |
                |    - Accuracy           |
                |    - No hallucination   |
                +-------------------------+
          +-------------------------------------+
          |         END-TO-END                  |
          |    - Full user journey              |
          |    - UI -> API -> Response          |
          +-------------------------------------+
    +---------------------------------------------------+
    |              INTEGRATION                          |
    |    - RAG pipeline                                 |
    |    - Vector store queries                         |
    |    - Prompt construction                          |
    +---------------------------------------------------+
+-----------------------------------------------------------+
|                     UNIT                                  |
|    - Input sanitization                                   |
|    - Token counting                                       |
|    - Response formatting                                  |
+-----------------------------------------------------------+
```

## Key Insight

**This pyramid is not new.** The best senior engineers have always structured their testing this way. What's new is the top layer: AI acceptance tests that evaluate probabilistic behavior rather than deterministic outputs.

Traditional tests verify that code works correctly. AI evals verify that the AI *behaves* correctly&mdash;that it uses the knowledge base appropriately, doesn't hallucinate information, provides accurate responses, and follows the expected format and tone.

## Risk Tiering

Not every feature needs the same depth of testing. Risk tiering helps teams apply the right level of governance based on impact:

| Tier | Risk Level | TSR Depth | Who Reviews | Example |
|------|-----------|-----------|-------------|---------|
| **Tier 1** | Low | Lightweight&mdash;automated test results only | Tech Lead | Internal tool, low-stakes suggestions |
| **Tier 2** | Medium | Standard&mdash;automated + sampled trace review | Tech Lead + Product Owner | Customer-facing chatbot, content generation |
| **Tier 3** | High | Full&mdash;comprehensive trace review + external audit | Governance Board + External | Medical advice, financial decisions, safety-critical |

Acme's support chatbot is **Tier 2**: customer-facing with moderate risk. Wrong pricing information is bad, but it won't endanger anyone's health.

## What the TSR Contains

The Test Summary Report has seven sections. Understanding this structure now helps you see where each phase's outputs end up:

1. **Change Summary** &mdash; What was changed and why
2. **Test Results** &mdash; Pass/fail rates across all test types
3. **Error Analysis** &mdash; The "money table"&mdash;axial code counts showing failure types and trends
4. **Changes Made** &mdash; How failures were addressed
5. **Remaining Risks** &mdash; Known issues and mitigations
6. **Monitoring Plan** &mdash; What to watch after deployment
7. **Go/No-Go Recommendation** &mdash; The decision, with evidence
