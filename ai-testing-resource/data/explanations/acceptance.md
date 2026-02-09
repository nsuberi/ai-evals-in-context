# Acceptance Tests

Acceptance tests verify that the system meets business requirements from the user's perspective. For example, an acceptance test confirms that a user can submit a question and receive a non-empty, professional response that addresses their topic. They ensure you're building the right thing, not just building it correctly.

## Relationship to AI
**For traditional software, acceptance tests verify requirements. For AI features, this is where evals come in.** A traditional acceptance test passes if *any* response is returned. AI evals extend this by checking whether the response is accurate, appropriately concise, and grounded in facts. AI evals are acceptance tests for AI behavior.
