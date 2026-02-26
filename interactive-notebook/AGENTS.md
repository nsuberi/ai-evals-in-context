# AI Agent Guidelines for interactive-notebook/

## Cost Management
- **Be strategic about which cells to run.** This notebook makes real API calls (Anthropic for RAG + evaluation, LangSmith for tracing). Each full run costs money.
- Only re-run cells that are affected by your changes. If you changed a helper function, re-run the helper cell + the cells that call it — not the entire notebook.
- When testing evaluation changes, use a single test case first before running the full parallel batch.
- The golden dataset (12 examples) and IRR traces (20 examples) each trigger multiple LLM judge calls. Avoid unnecessary re-runs of these sections.

## Execution Time
- Always write code to minimize end-to-end notebook execution time.
- Use `ThreadPoolExecutor` for independent API calls (already done for evaluation cells).
- When adding new sections, use the same parallel patterns established in the helper functions.
- Keep `max_tokens` as low as reasonable for test/demo calls.

## Copying Metrics for Thread Safety
- deepeval metrics contain an `AnthropicModel` which wraps an `anthropic.Anthropic()` client. That client uses `httpx.Client` internally, which holds `_thread.RLock` objects. **`deepcopy` will fail** with `TypeError: cannot pickle '_thread.RLock' object`.
- Use `copy.copy` (shallow copy) for metrics before calling `measure()`. This is safe because `measure()` only assigns new scalar attributes (`self.score`, `self.reason`, `self.success`) — it does not mutate shared mutable containers on the original.
- The shared model reference is fine: the Anthropic/httpx client is thread-safe for concurrent reads.

## Verification
- **Always check Jupyter cell output after running.** Do not assume code works from syntax alone. When modifying cells, re-run them and inspect the output (DataFrames, print statements, error traces) before declaring success.
- When refactoring evaluation cells, verify that the output DataFrames have the same shape and column names as before the refactor.
