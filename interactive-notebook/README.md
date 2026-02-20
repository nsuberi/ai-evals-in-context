# AI Evaluation Workshop Notebook

A hands-on Jupyter notebook that teaches AI evaluation concepts using **deepeval**, a local **ChromaDB** RAG pipeline, and **Claude** as both the response generator and LLM judge. All examples use a mortgage lending domain.

## Prerequisites

- Python 3.12+
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

```bash
cd interactive-notebook/

# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file (if it doesn't already exist)
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env

# 4. Launch the notebook
jupyter notebook ai_eval_workshop.ipynb
```

## What You'll Learn

| Section | Topic | Key Concept |
|---------|-------|-------------|
| 1 | Assertions & Basic deepeval | RAG pipeline evaluation with generic metrics (faithfulness, relevancy, precision, recall) |
| 2 | Custom Metrics | Domain-specific GEval metrics for regulatory compliance and actionability |
| 3 | Golden Dataset | Acceptance criteria with positive and negative examples |
| 4 | Inter-Rater Reliability | Cohen's kappa — validating that your automated judge agrees with human judgment |
| 5 | Multiple Evaluators | Pairwise and Fleiss' kappa across product, compliance, and LLM raters |
| 6 | Production Monitoring | Improvement loops, trace capture, governance as accelerator |

## API Cost

Running the full notebook costs approximately **$2-5** using Claude Sonnet. The majority of API calls happen in Sections 1-3 (RAG generation + metric evaluation). Sections 4-5 use pre-written responses to keep costs predictable.

## Troubleshooting

**deepeval login prompt:** The notebook sets `DEEPEVAL_TELEMETRY_OPT_IN=NO` in the first code cell. If you still see a login prompt, run this in your terminal before launching:
```bash
export DEEPEVAL_TELEMETRY_OPT_IN=NO
```

**ChromaDB first-run download:** ChromaDB downloads its default ONNX embedding model (~80MB) on first use. This is a one-time download.

**Missing API key:** If you see authentication errors, verify your `.env` file is in the same directory as the notebook and contains a valid `ANTHROPIC_API_KEY`.

**Kernel not found:** Make sure you installed `ipykernel` and are selecting the correct virtual environment kernel. You can register it explicitly:
```bash
python3 -m ipykernel install --user --name=ai-eval-workshop
```
