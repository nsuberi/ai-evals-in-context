# AI Acceptance Testing

AI Acceptance tests define the minimum acceptable behavior for AI features. For example, an AI acceptance test verifies that every chatbot response cites at least one source document and that the grounding score meets the 85% threshold agreed upon with stakeholders. Unlike traditional acceptance tests with binary pass/fail, AI acceptance tests use statistical thresholds to account for non-deterministic outputs.

## Relationship to AI
**AI acceptance tests are the guardrails; AI evals are the quality measurement.** Acceptance tests define hard requirements that must not be crossed (responses must cite sources, no hallucinated medical advice). Evals measure quality distribution across many cases for continuous improvement. Human-in-the-loop validation from subject matter experts defines what "good" means and sets the thresholds.
