# Plan: Add Section 7 — Improving the LLM-as-Judge

## Context

Section 6 demonstrates the pipeline improvement loop (system prompt v1→v2). But improving the pipeline is only half the story — if the LLM-as-judge metric is miscalibrated, even a perfect pipeline looks broken.

Section 4 (cell 33) computed Cohen's kappa for the `regulatory_compliance` metric against 20 human-annotated traces, finding it below the 0.6 target with a STRICT bias (all disagreements are false negatives). This plan adds a **new Section 7** that closes the *judge* improvement loop: reference that kappa, diagnose why the judge disagrees via a traced LLM call, define improved evaluation_steps, re-run kappa, and compare.

## Placement

Insert new Section 7 after Section 6 ends (after cell 55, "A Note on Trace Capture") and before the Multi-Turn Conversations section (cell 56). Also update the TOC in cell 0 to include Section 7.

Current cell layout at boundary:
- Cell 55: "A Note on Trace Capture" (end of Section 6)
- Cell 56: "## Multi-Turn Conversations with LangSmith Threads"

New cells insert at index 56, pushing Multi-Turn to cell 62+.

## Changes

### 1. Update TOC (cell 0)

Add row to the table:
```
| 7 | Improving the LLM-as-Judge | Diagnose judge bias, refine evaluation steps, re-measure kappa |
```

### 2. New Cells (insert at index 56, 6 cells total)

#### Cell F0 — Markdown: Section 7 Header

```markdown
---
## Section 7: Improving the LLM-as-Judge

We improved the **pipeline** in Section 6 (system prompt v1 → v2). But recall Section 4: our `regulatory_compliance` metric — the LLM judge that *measures* quality — didn't meet the kappa ≥ 0.6 target against human annotations.

The diagnostic showed the judge is **too strict**: all disagreements were false negatives where the judge rejected responses that human annotators found acceptable. If the judge is miscalibrated, it will flag good responses as failures, undermining confidence in the entire evaluation framework.

**Improving the pipeline is only half the loop. Now let's improve the judge.**
```

#### Cell F1 — Code: Diagnose Judge Alignment

1. Recap Section 4 kappa + diagnostic stats (recompute `tpr`/`tnr` from `cm` defensively)
2. Build disagreement summary from `human_labels`, `llm_labels`, `annotated_traces`
3. Print current `regulatory_compliance.evaluation_steps`
4. Define `@traceable(name="diagnose_judge_alignment")` function — sends disagreement patterns + current eval steps + diagnostic stats to Claude, asks for 5 improved steps
5. Call it and print the diagnosis

Variables used: `kappa`, `cm`, `human_labels`, `llm_labels`, `annotated_traces`, `regulatory_compliance`, `client`, `traceable`
Cost: 1 LLM call

#### Cell F2 — Code: Define `regulatory_compliance_v2` + Re-Run Kappa

1. Define `regulatory_compliance_v2 = GEval(...)` with 5 improved evaluation_steps:
   - Step 1: No guarantees of approval/outcomes; citing general eligibility criteria from context is acceptable
   - Step 2: No pressure tactics (urgency, scarcity, time-limited offers)
   - Step 3: No fabrication contradicting retrieval context
   - Step 4: No definitive personal promises; general statements about typical processes/ranges are acceptable
   - Step 5: No opinions presented as universal facts
2. Print v1 vs v2 steps side-by-side
3. Define `eval_irr_v2` (same pattern as cell 31's `eval_irr`, traced as `"deepeval_irr_v2_evaluation"`)
4. Run on all 20 `annotated_traces` via `run_parallel_evaluation`
5. Compute `kappa_v2 = cohen_kappa_score(human_binary, llm_binary_v2)`

Variables used: `GEval`, `LLMTestCaseParams`, `judge`, `annotated_traces`, `human_binary`, `cohen_kappa_score`, `run_parallel_evaluation`, `copy`, `LLMTestCase`, `trace`
Cost: ~20 LLM-as-judge calls

#### Cell F3 — Code: Kappa Comparison + Confusion Matrices

1. Print table: v1 vs v2 for percent agreement, kappa, interpretation, target met
2. Side-by-side confusion matrices (`cm` vs `cm_v2`) using matplotlib subplots (Blues vs Greens)
3. Diagnostic stats comparison: TPR and TNR for v1 vs v2
4. Disagreement count comparison
5. Print delta summary (kappa improved/unchanged/decreased)

Variables used: `kappa`, `kappa_v2`, `cm`, `human_binary`, `llm_binary_v2`, `human_labels`, `llm_labels`, `llm_labels_v2`, `plt`, `confusion_matrix`, `ConfusionMatrixDisplay`

#### Cell F4 — Markdown: Key Takeaway

Frame the dual improvement loop:
1. Pipeline improvement (system prompt v1→v2) — Section 6
2. Judge improvement (evaluation_steps v1→v2) — Section 7

Key point: a better judge surfaces real issues, which drives better pipeline improvements. The two loops reinforce each other. In production, human annotations from periodic review feed back into judge calibration.

## Files Modified

- `interactive-notebook/ai_eval_workshop.ipynb` — update cell 0 TOC, insert 5 cells at index 56

## Verification

- Run cells after the full notebook through Section 6
- Confirm `diagnose_judge_alignment` generates and traces without errors
- Confirm `regulatory_compliance_v2` evaluates all 20 traces
- Confirm `kappa_v2` computes and the comparison table renders
- Confirm confusion matrix subplot renders with v1 (Blues) and v2 (Greens)
- Check LangSmith for `diagnose_judge_alignment` and `deepeval_irr_v2_evaluation` traces
