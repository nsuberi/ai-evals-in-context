## Iteration Is How Experienced Engineers Have Always Shipped Quality Software

Before deploying to production, we iterate on the chatbot's behavior through multiple versions. Each version addresses failure modes discovered through AI evaluations and trace inspection. This is the same build-test-fix cycle that experienced engineers follow for any feature&mdash;the difference with AI is that you're tuning behavior, not just fixing bugs.

**The Iteration Cycle:**
1. Run evaluations against the current version
2. Identify failure modes (too verbose, hallucinating, missing sources)
3. Adjust the prompt strategy or architecture (e.g., add RAG)
4. Re-run evaluations and inspect traces
5. Repeat until all acceptance criteria pass

**Open Code &rarr; Axial Code Methodology:** The trace annotations below use a two-level coding scheme. Each trace gets *open codes*&mdash;free-text observations specific to that trace (e.g., "Price stated as $349, actual is $299"). These are then categorized into *axial codes*&mdash;standardized labels that can be counted across traces (e.g., "Factual Hallucination"). This quantification turns subjective quality assessment into objective evidence for the TSR.

**Practical Workflow (4 weeks):**

- **Week 1:** Trace collection&mdash;capture representative interactions across test scenarios
- **Week 1-2:** Error analysis in the review interface&mdash;open coding (annotating traces with free-text observations)
- **Week 2:** Failure taxonomy and counting&mdash;axial coding (categorizing observations into quantifiable codes)
- **Week 2-3:** Fix &rarr; Test &rarr; Document&mdash;axial code counts become the "money table" in TSR Section 3

Select a version to see its failure modes, architecture decisions, and sample traces.
