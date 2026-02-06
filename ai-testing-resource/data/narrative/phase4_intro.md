## Building AI Features Through Iteration

Before deploying to production, we iterate on the chatbot's behavior through multiple versions. Each version addresses failure modes discovered through AI evaluations and trace inspection.

**The Iteration Cycle:**
1. Run evaluations against the current version
2. Identify failure modes (too verbose, hallucinating, missing sources)
3. Adjust the prompt strategy or architecture (e.g., add RAG)
4. Re-run evaluations and inspect traces
5. Repeat until all acceptance criteria pass

Select a version to see its failure modes, architecture decisions, and sample traces. The annotations highlight exactly where each version succeeds or fails.
