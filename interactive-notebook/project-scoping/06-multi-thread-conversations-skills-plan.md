# Plan: Restructure End of Notebook (Cells 59–69 → 59–71)

## Context

After the Section 7 wrap-up (cell 58, "What We Built — and Where It Goes From Here"), the notebook has a disjointed sequence: Multi-Turn Conversations, a "What We Built" summary table, a final summary code cell, LangSmith Trace Validation cells, and an empty cell. The user wants this restructured so the ending feels informative and cohesive, with Multi-Turn framed as an appendix and a new discussion on what multi-turn evaluation requires beyond single-turn.

## Current Layout (cells 59–69)

| Cell | Type | Content |
|------|------|---------|
| 59 | md | `## Multi-Turn Conversations with LangSmith Threads` intro |
| 60 | code | `chat_mortgage_assistant` function |
| 61 | code | 3-turn conversation execution |
| 62 | md | LangSmith threads view explanation |
| 63 | md | `### What We Built` summary table |
| 64 | code | Final summary print block |
| 65 | md | `### LangSmith Trace Validation` header |
| 66 | code | Query LangSmith traces |
| 67 | code | RAG trace hierarchy verification |
| 68 | code | Evaluation trace outputs |
| 69 | code | empty |

## New Layout (cells 59–71)

### Main narrative conclusion (right after cell 58)

**Cell 59 — md: "What We Built" summary table** (from old 63)
- Update table to add row for Section 7: judge improvement, refined evaluation steps, kappa recalibration

**Cell 60 — code: Final summary** (from old 64)
- Add `kappa_v2` line to the print block

### Appendix A: Multi-Turn Conversations

**Cell 61 — md: Appendix A header** (rewrite of old 59)
- `---` + `## Appendix A: Multi-Turn Conversations`
- Reframe: explains that the workshop focused on single-turn evaluation; this appendix demonstrates extending the same RAG pipeline to multi-turn and raises open questions

**Cell 62 — code: `chat_mortgage_assistant`** (old 60, unchanged)

**Cell 63 — code: 3-turn conversation** (old 61, unchanged)

**Cell 64 — md: LangSmith threads explanation** (old 62, unchanged)

**Cell 65 — md: NEW — "Evaluating Multi-Turn: What Transfers and What Doesn't"**
- **What transfers directly from Sections 1–7:**
  - Per-turn evaluation: each turn is still a one-shot request with input/output/retrieval_context — existing metrics (faithfulness, relevancy, regulatory compliance) apply to each turn individually
  - IRR methodology: annotate individual turns, compute kappa, same calibration loop
  - Improvement loops: prompt refinement and judge refinement work the same way per-turn
- **What requires additional techniques:**
  - Conversation-level quality: coherence across turns, pronoun resolution ("that same loan type"), context maintenance — need metrics that evaluate the *thread* as a unit. Example from our 3-turn conversation: Turn 2 references "that same loan type" — faithfulness per-turn doesn't check whether the assistant correctly resolved the reference back to FHA
  - Growing context window: token usage and cost grow per-turn; retrieval relevance may shift as the conversation narrows scope
  - Stateful failure modes: errors compound — a slightly wrong Turn 1 answer becomes bad context in Turn 3. Our per-turn metrics would flag Turn 3 but miss that the root cause was Turn 1
  - Knowledge base coverage: multi-turn probes the KB from different angles in sequence — coverage gaps surface differently than one-shot
  - Memory: production multi-turn systems often use conversation memory — summarized or compressed history — to manage context window limits. This introduces a new evaluation surface: does a memory summary preserve the details needed for accurate follow-up answers? Our current per-turn evaluation doesn't account for information loss through summarization.
  - Caching: production systems cache at multiple levels to reduce latency and cost. Each layer introduces its own staleness risk:
    - *Retrieval-level caching*: if Turn 1 retrieves "FHA loan requirements," the system may cache those results and serve them for Turn 2's FHA follow-up instead of re-querying ChromaDB. This works until the conversation shifts — if Turn 3 asks "what about VA loans instead?" and the system serves the cached FHA docs, the assistant answers from wrong context. It might cite FHA down payment rules (3.5%) when the borrower is asking about VA (which can offer 0% down). Our faithfulness metric would still pass because the response *is* faithful to the provided context — it's just the wrong context for the current question.
    - *LLM API-level caching*: services like Anthropic's prompt caching let you cache the system prompt and long context prefixes so they aren't re-processed on every call. In multi-turn, this means conversation history up to a certain point gets cached as a prefix. If the system prompt or retrieval context changes mid-conversation (e.g. the v2 prompt from Section 6 gets deployed, or retrieval results shift), the cached prefix may contain stale instructions or outdated context that the LLM treats as authoritative.
    - *Embedding-level caching*: some systems cache the vector embeddings of user queries to skip re-embedding similar questions. If a user rephrases their question in Turn 3 ("actually, tell me about veteran loan options" vs "what about VA loans?"), the cached embedding from the earlier phrasing may retrieve different — and potentially less relevant — documents than a fresh embedding would.
    - The common thread: caching optimizes for the *previous* state of the conversation. Evaluation needs to check whether the cached artifacts still match the *current* turn's intent and context.
- **Open research areas for systematic improvement:**
  - Thread-level GEval metrics — evaluate whole conversations against coherence/consistency criteria
  - Conversation-aware golden datasets — annotated threads, not isolated Q&A pairs. Needs both per-turn and whole-thread labels
  - Turn-position-aware IRR — does the judge perform differently on Turn 1 vs Turn 5? Kappa may vary by position
  - Progressive context evaluation — does retrieval quality degrade as conversation history grows?
  - Multi-turn improvement loops — which prompt changes help conversation coherence vs just per-turn quality?
  - Memory fidelity evaluation — when conversation history is summarized or compressed, does the summary preserve facts accurately? A borrower who mentioned a 580 credit score in Turn 1 shouldn't become "good credit" in a Turn 5 summary
  - Cache-aware evaluation — metrics that verify cached artifacts (retrieval results, embeddings, prompt prefixes) still align with the current turn's intent, not just the turn they were originally computed for. This spans retrieval-level, LLM API-level, and embedding-level caching
- Close: the single-turn framework from Sections 1–7 provides the foundation; multi-turn adds a temporal dimension — and memory/caching add an infrastructure dimension — that require purpose-built evaluation techniques. This is an active area — the tools (LangSmith threads, deepeval, kappa) are ready, but the methodology for systematic multi-turn judge calibration is still developing.

### Appendix B: LangSmith Trace Validation

**Cell 66 — md: header** (from old 65, retitle to `## Appendix B: LangSmith Trace Validation`)

**Cell 67 — code: Query traces** (old 66, unchanged)

**Cell 68 — code: RAG hierarchy** (old 67, unchanged)

**Cell 69 — code: Evaluation trace outputs** (old 68, unchanged)

**Cell 70 — code: empty** (old 69, unchanged)

## Implementation

Replace all cells from index 59 onward in one Python script operation to avoid index confusion. Build the new cell list, then assign `nb['cells'] = nb['cells'][:59] + new_cells`.

## Files Modified

- `interactive-notebook/ai_eval_workshop.ipynb` — restructure cells 59 onward

## Verification

- Confirm total cell count is 71
- Confirm ordering: 58 (wrap-up) → 59 (table) → 60 (summary) → 61 (appendix A) → 62-63 (code) → 64 (threads md) → 65 (discussion) → 66 (appendix B) → 67-69 (code) → 70 (empty)
- Validate Python syntax on all code cells
- Read cell 65 for coherence of the multi-turn discussion
