# AI Evaluations

AI Evals are acceptance tests for AI behavior. They verify that AI outputs meet quality criteria such as accuracy, appropriate length, factual grounding, and format compliance. For example, an eval checks whether the chatbot's pricing answers contain the correct dollar amounts from the knowledge base rather than hallucinated figures.

Unlike traditional tests, evals are often statistical ("80% of responses should be under 100 words"), use LLMs to evaluate LLM outputs, and run continuously to detect behavioral drift.

## Relationship to AI
**AI Evals sit at the acceptance level of the testing pyramid because they verify user-facing quality.** They require more test cases for statistical significance, tolerance for variation rather than binary pass/fail, and continuous monitoring since AI behavior can change over time. They drive the iterative improvement cycle: deploy, collect traces, annotate failures, fix, and verify.
