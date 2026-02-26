# Plan: Add "Improvement in Action" Demo to Section 6

## Context

Section 6 discusses the improvement loop conceptually (ASCII diagram, governance framing) but never demonstrates it with code. The notebook has already computed `df_full` (5 metrics × 4 scenarios), `df_contrast` (contrived non-compliant response), `kappa` (IRR), and disagreement analysis. This section closes the loop: diagnose from the existing metrics, make a targeted prompt improvement, re-evaluate, and compare.

## Placement

Insert 5 cells after cell 48 (The Improvement Loop ASCII diagram), before cell 49 (Governance as Accelerator). Flow: conceptual loop → **concrete demo** → governance framing.

## Available Variables

All of these are defined by earlier cells and available at this point:
- `test_questions` (cell 10) — 4 scenario dicts with `input`, `expected_output`, `scenario`
- `all_metrics` (cell 18) — [faithfulness, relevancy, precision, regulatory_compliance, actionability]
- `df_full` (cell 18) — full metric results, indexed by scenario
- `df_contrast` (cell 19) — contrived problematic response results
- `kappa` (cell 33) — Cohen's kappa
- `collection` (cell 4) — ChromaDB
- `client` (cell 6) — wrapped Anthropic client
- `MORTGAGE_DOCS` (cell 3) — raw docs
- `LLMTestCase` (cell 10)
- Helpers: `evaluate_and_trace`, `run_parallel_evaluation`, `get_metric_name`, `copy` (cell 11)
- `traceable`, `trace` (cell 6)

## New Cells

### Cell A — Markdown intro
```markdown
### Closing the Loop: From Observation to Improvement

The improvement loop diagram above is abstract — let's make it concrete. We'll:
1. **Diagnose** — review the metric results from Sections 1–2 to identify a pattern
2. **Improve** — make a targeted change to the system prompt
3. **Re-evaluate** — run the same test cases and metrics
4. **Compare** — measure whether the change helped
```

### Cell B — Code: Diagnose from existing results
Read `df_full` and `df_contrast` (no API calls). Print:
- Count of FAILs per metric across the 4 scenarios
- Highlight that the contrived example passed generic metrics but failed custom ones
- Identify the pattern: responses may lack explicit disclaimers or use insufficiently hedged language

### Cell C — Code: Improved pipeline + re-evaluation
1. Define `ask_mortgage_assistant_v2` with `@traceable` — same RAG retrieval logic, but improved system prompt with:
   - Numbered rules (easier for the model to follow)
   - Explicit prohibition on rate quotes and timeline guarantees
   - Required structure: always end with a disclaimer/recommendation
   - Stronger hedging requirements
2. Generate new answers for the same 4 `test_questions`
3. Build test cases and evaluate with `all_metrics` via `run_parallel_evaluation`

Cost: ~4 RAG calls + ~20 evaluation calls.

### Cell D — Code: Before/after comparison
- Merge v1 (`df_full`) and v2 results into a side-by-side DataFrame
- Show per-metric improvement counts
- Print summary: "X metrics improved, Y unchanged, Z regressed"

### Cell E — Markdown takeaway
Connect back to the loop: we completed one iteration. In production, this repeats with real traces — new edge cases become golden examples, disagreements trigger calibration, the prompt evolves.

## Files Modified
- `interactive-notebook/ai_eval_workshop.ipynb` — insert 5 cells after current cell 48

## Verification
- Run cells A–E after the full notebook through Section 5
- Confirm v2 answers generate and evaluate without errors
- Confirm comparison DataFrame renders with before/after columns
- Check LangSmith for v2 evaluation traces
