# Plan: Standalone AI Evaluation Workshop Notebook

## Context

This notebook is a standalone supplementary resource that teaches AI evaluation concepts using deepeval, a local Chroma RAG pipeline, and Claude as both the generator and LLM judge. The organization currently has no trace capture capability, so the notebook uses synthetic data throughout.

**Key narrative thread:** Governance is an accelerator, not a gate. Confidence in automated evaluation comes from systematically comparing machine judgment against human judgment.

## Deliverables

All files go in the existing `interactive-notebook/` directory at the repo root. The `.env` with `ANTHROPIC_API_KEY` is already there. Completely standalone — no imports from the existing codebase.

```
interactive-notebook/
  .env                     # Already exists with ANTHROPIC_API_KEY
  ai_eval_workshop.ipynb   # The Jupyter notebook (6 sections, ~59 cells)
  requirements.txt         # Pinned dependencies
  README.md                # Setup instructions
```

## requirements.txt

```
deepeval>=3.8
chromadb>=1.0
anthropic>=0.80
scikit-learn>=1.6
statsmodels>=0.14
matplotlib>=3.10
seaborn>=0.13
pandas>=2.2
numpy>=2.2
ipykernel>=6.29
python-dotenv>=1.0
```

Uses minimum version pins (not exact) for broader compatibility. No LangChain, no OpenAI SDK. ChromaDB bundles its own ONNX embedding model (~80MB downloaded on first use).

## README.md

Brief setup guide covering:
- Prerequisites: Python 3.12+, Anthropic API key
- Steps: create venv, pip install, create `.env`, launch notebook
- What you'll learn (section overview)
- API cost estimate (~$2-5 using Claude Sonnet for full run)
- Troubleshooting (telemetry opt-out, ChromaDB download, missing key)

## Notebook Structure

### Preamble (2 cells)
- **[MD]** Title, workshop overview, section roadmap table
- **[Code]** Environment setup: load `.env`, verify API key, set `DEEPEVAL_TELEMETRY_OPT_IN=NO`

### Section 1: Assertions and Basic deepeval (~12 cells)
- **[MD]** Frame AI eval as assertions — connect to classical testing terminology
- **[Code]** Define 4 mortgage knowledge base documents as Python strings (loan types, rate locks, escrow/closing, underwriting/compliance — each ~400 words, mortgage-specific)
- **[Code]** Load documents into ChromaDB ephemeral client
- **[MD]** Explain the RAG pipeline (retrieve + generate)
- **[Code]** Define `ask_mortgage_assistant()` — queries ChromaDB, calls Claude Sonnet
- **[Code]** Test with a sample question
- **[MD]** Introduce deepeval metrics table (faithfulness, answer relevancy, contextual precision/recall)
- **[Code]** Set up `AnthropicModel` as judge, instantiate 4 generic metrics
- **[Code]** Create 4 test cases covering: straightforward factual, wrong-context retrieval, multi-doc, compliance-sensitive
- **[Code]** Run metrics, display results in pandas DataFrame
- **[MD]** "The Gap" — what generic metrics miss (regulatory disclaimers, tone, promises, actionability)

### Section 2: Custom Metrics (~8 cells)
- **[MD]** Why custom metrics — domain-specific quality for mortgage lending
- **[Code]** Build `GEval` metric: "Regulatory Compliance" (5 evaluation steps: no guarantees, hedging language, no bare rate quotes, loan officer referral, no binding commitments)
- **[Code]** Build `GEval` metric: "Actionability" (4 evaluation steps: specificity, next steps, numerical values, clear path forward)
- **[Code]** Run all metrics (generic + custom) side by side on same test cases
- **[Code]** Contrived example: technically faithful but regulatorily problematic response — show generic passes, custom fails
- **[MD]** "What Just Happened?" — explain the divergence
- **[MD]** Key takeaway: custom metrics encode tribal knowledge into automated assertions

### Section 3: Golden Dataset and Acceptance Criteria (~7 cells)
- **[MD]** What a golden dataset is — acceptance criteria, regression testing, alignment artifact. Must include positive AND negative examples.
- **[Code]** Define 12 golden examples using `EvaluationDataset` + `Golden`: 8 positive (hedged, compliant, actionable) + 4 negative (approval guarantee, vague non-answer, hallucinated policy, bare rate quote)
- **[MD]** The human annotation workflow — collect, rate, discuss disagreements, lock
- **[Code]** Generate actual outputs via RAG, evaluate against golden dataset
- **[Code]** Analyze: do negative examples actually score lower? Show averages by label.
- **[MD]** Transition: "How much can we trust these automated scores?"

### Section 4: Inter-Rater Reliability — Single Evaluator Pair (~11 cells)
- **[MD]** Validating the validator — Cohen's kappa, medicine analogy table
- **[MD]** Introduce simulated human annotations
- **[Code]** Define 20 pre-written traces with human labels (7 clearly acceptable, 5 clearly unacceptable, 8 borderline). Pre-written responses (not live-generated) so annotations stay valid across runs.
- **[Code]** Run regulatory compliance metric on all 20, convert scores to binary labels at threshold 0.7
- **[MD]** Explain Cohen's kappa formula, interpretation table (poor through almost perfect), target: kappa >= 0.6
- **[Code]** Calculate Cohen's kappa via `sklearn.metrics.cohen_kappa_score`
- **[Code]** Build and visualize confusion matrix with `ConfusionMatrixDisplay`
- **[Code]** Calculate TPR (sensitivity), TNR (specificity), PPV, NPV with plain-English interpretations
- **[MD]** What these numbers mean: high TPR/low TNR = lenient judge, and vice versa. For regulatory compliance, optimize for TNR.
- **[Code]** Show specific disagreement traces with reasons
- **[MD]** Key takeaway: IRR is the bridge between "we built a metric" and "we trust this metric"

### Section 5: Multiple Evaluators — Bonus (~9 cells)
- **[MD]** Scaling evaluation: product team, compliance officer, automated LLM judge
- **[Code]** Define 15-trace multi-rater dataset (3 raters). Designed so product+LLM agree well (~0.65-0.75), compliance is stricter (~0.45-0.60 with others).
- **[Code]** Calculate pairwise Cohen's kappa for all 3 pairs
- **[Code]** Visualize as a kappa heatmap (seaborn)
- **[Code]** Calculate Fleiss' kappa via `statsmodels.stats.inter_rater`
- **[Code]** 3-subplot confusion matrices for each evaluator pair
- **[MD]** Business decisions table: agreement patterns map to work distribution strategies
- **[Code]** Summary statistics table with AUTOMATE/HUMAN REVIEW recommendations
- **[MD]** Key takeaway: low Fleiss' kappa means the team needs calibration, not that the metric is bad

### Section 6: Production Monitoring and Improvement Loops (~6 cells)
- **[MD]** Three monitoring approaches: user feedback (low effort), scheduled review (medium), automated agents (high). Mostly narrative, light on code.
- **[MD]** ASCII improvement loop diagram: Golden Dataset → Automated Eval → Deploy → Monitor → Discover → Update Golden Dataset
- **[MD]** Governance as accelerator: with framework, changes validated in minutes, decisions based on evidence not opinions
- **[MD]** Note on trace capture: path from synthetic data → anonymized traces → aggregate metrics → graduated rollout
- **[MD]** Summary table: what we built, what each component does, what tool implements it
- **[Code]** Final summary statistics print

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Pre-written responses in Sections 4-5 | If responses changed between runs, human annotations would be meaningless |
| ChromaDB ephemeral (in-memory) client | No disk artifacts; rebuilds in seconds |
| Claude Sonnet as both generator and judge | Single API key, consistent behavior; note in notebook that production may use different models |
| `metric.measure()` not `evaluate()` | Pedagogical clarity — explicit control flow, custom result tables |
| `DEEPEVAL_TELEMETRY_OPT_IN=NO` | No login prompts or cloud dependencies |
| Mortgage domain for sample data | Directly relevant to audience's industry |
| Min version pins, not exact | Better cross-platform compatibility with Python 3.12 |

## Implementation Sequence

1. Create `interactive-notebook/` directory
2. Write the 4 mortgage knowledge base document strings
3. Write the 12 golden dataset entries
4. Write the 20 annotated traces (Section 4)
5. Design the 15 multi-rater annotations (Section 5)
6. Build the notebook cell by cell (markdown narrative + code)
7. Write `requirements.txt`
8. Write `README.md`
9. Test from scratch: fresh Python 3.12 venv → pip install → `.env` → run all cells
10. Save notebook with outputs so non-API users can read it

## Verification

1. Create a fresh Python 3.12 virtual environment inside `interactive-notebook/`
2. `pip install -r requirements.txt` — verify no dependency conflicts
3. `.env` with `ANTHROPIC_API_KEY` already exists in the directory
4. `jupyter notebook ai_eval_workshop.ipynb` — run all cells top to bottom
5. Verify: ChromaDB loads, RAG pipeline returns answers, deepeval metrics score, confusion matrices render, kappa values compute
6. Check API cost on Anthropic dashboard (should be ~$2-5)
