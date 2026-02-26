# Plan: Add `metadata_extra` to `evaluate_and_trace`, Merge Golden Trace Names

## Context

`evaluate_and_trace` (cell 11) currently accepts fixed metadata keys (`section`, `label`). Callers needing extra metadata like `prompt_version` had to either bypass the function entirely (cell 53 duplicates its internals) or skip it. This makes the code harder to follow for non-coders — there are two evaluation patterns that do the same thing.

The refactor: add an optional `metadata_extra` parameter to `evaluate_and_trace`, eliminate the structural duplicate in cell 53, and merge the `deepeval_golden_pipeline` trace name into `deepeval_golden_dataset` (distinguished by `prompt_version` metadata).

## Changes

### Cell 11: Add `metadata_extra` to `evaluate_and_trace`

Add `metadata_extra=None` parameter. Merge it into the trace metadata dict:
```python
def evaluate_and_trace(index, test_case, metrics, trace_name, section, label, metadata_extra=None):
    ...
    metadata = {"section": section, "label": label}
    if metadata_extra:
        metadata.update(metadata_extra)
    with trace(..., metadata=metadata) as eval_run:
```

### Cell 18: Pass `prompt_version` to V1 evaluation

```python
def eval_all(i, tc):
    return evaluate_and_trace(i, tc, all_metrics, "deepeval_all_metrics",
                              "all_metrics", test_questions[i]["scenario"],
                              metadata_extra={"prompt_version": "v1"})
```

### Cell 51: Pass `prompt_version` to V2 evaluation

```python
def eval_v2(i, tc):
    return evaluate_and_trace(i, tc, all_metrics, "deepeval_v2_metrics",
                              "improvement_v2", test_questions[i]["scenario"],
                              metadata_extra={"prompt_version": "v2"})
```

### Cell 53: Rewrite to use `evaluate_and_trace` + merge trace name

- Delete the `eval_golden_pipeline` function (structural duplicate)
- Use `evaluate_and_trace` directly via simple wrappers
- Change trace name from `"deepeval_golden_pipeline"` → `"deepeval_golden_dataset"`
- Pass `metadata_extra={"prompt_version": "v1"}` / `"v2"`

### Cell 72 (Appendix B): Update query filter

Change from querying `deepeval_golden_pipeline` to querying `deepeval_golden_dataset` with `prompt_version` in metadata (distinguishes pipeline evals from the pre-written eval in cell 25, which has no `prompt_version`).

### Cells 13, 25: No change

- Cell 13 (`eval_generic`): first-pass evaluation, no version comparison needed
- Cell 25 (`eval_golden`): evaluates pre-written answers, `prompt_version` doesn't apply

### Cells 31, 57: No change

IRR evaluations use inline `trace()` because they have different return structures (single metric, score/verdict format). They already carry `judge_version` metadata. Separate pattern is justified here — single-metric IRR is genuinely different from multi-metric evaluation.

## Files Modified

- `interactive-notebook/ai_eval_workshop.ipynb` — cells 11, 18, 51, 53, 72

## Verification

- Validate Python syntax on all modified cells
- Confirm `evaluate_and_trace` signature is backward-compatible (existing callers without `metadata_extra` still work)
- Confirm no remaining references to `deepeval_golden_pipeline`
- Confirm cell 53 no longer defines `eval_golden_pipeline` function
