# Testing Strategy - Where AI Evals Fit

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

**AI Evals are acceptance tests for AI behavior.** They sit at the top of the pyramid and validate that the AI system meets requirements like accuracy, grounding, and appropriate response format.

Traditional tests verify that code works correctly. AI evals verify that the AI *behaves* correctly - that it:

- Uses the knowledge base appropriately
- Doesn't hallucinate information
- Provides accurate, helpful responses
- Follows the expected format and tone
