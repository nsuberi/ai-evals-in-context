"""Iteration Timeline - Compare versions and show evolution"""

from typing import Dict, List
from .trace_inspector import get_trace_summary, AXIAL_CODES  # noqa: F401

FAILURE_MODES = {
    "v1": [
        {
            "id": "fm-v1-01",
            "name": "Response too verbose",
            "severity": "warning",
            "description": (
                '20/20 traces annotated with "Length Violation". '
                "System prompt asks for 300+ word responses. "
                "Users want concise ~80 word answers for quick support."
            ),
            "resolution": "Updated prompt constraints in v2 to request approximately 80 words.",
        },
        {
            "id": "fm-v1-02",
            "name": "No source attribution",
            "severity": "warning",
            "description": (
                "Responses never cite knowledge base documents. "
                "Users cannot verify the accuracy of information provided."
            ),
            "resolution": "Added RAG pipeline in v3 with source citation.",
        },
    ],
    "v2": [
        {
            "id": "fm-v2-01",
            "name": "Price hallucination",
            "severity": "error",
            "description": (
                'Multiple traces annotated with "Factual Hallucination". '
                "Model fabricates pricing details (e.g., $349 instead of $299 for Enterprise, "
                "$59 instead of $49 for Starter)."
            ),
            "resolution": "RAG grounding in v3 ensures prices come from knowledge base documents.",
        },
        {
            "id": "fm-v2-02",
            "name": "Specification hallucination",
            "severity": "error",
            "description": (
                'Traces annotated with "Factual Hallucination". '
                "Fabricates product specifications like weight, battery capacity, materials, "
                "and water resistance ratings."
            ),
            "resolution": "Knowledge base retrieval in v3 provides accurate product data.",
        },
        {
            "id": "fm-v2-03",
            "name": "Policy hallucination",
            "severity": "error",
            "description": (
                'Traces annotated with "Factual Hallucination". '
                "Invents wrong return shipping fees ($9.99 vs $8.95), refund timelines "
                "(3-5 vs 5-7 days), and shipping thresholds."
            ),
            "resolution": "RAG grounding in v3 retrieves actual company policies.",
        },
        {
            "id": "fm-v2-04",
            "name": "Missing source attribution",
            "severity": "warning",
            "description": (
                '20/20 traces annotated with "Missing Source Attribution". '
                "No KB citations provided, so users cannot verify any information."
            ),
            "resolution": "RAG pipeline in v3 injects KB context and cites sources.",
        },
    ],
    "v3": [],
}

ARCHITECTURE_CONTEXT = {
    "v1": {
        "prompt_strategy": "Direct Claude API call with a verbose system prompt requesting 300+ word responses.",
        "architecture": "Simple request-response: user question goes directly to Claude with no retrieval or grounding.",
        "known_limitations": "No access to company data. Model relies entirely on training data, leading to generic responses.",
    },
    "v2": {
        "prompt_strategy": "Updated prompt to request concise ~80 word responses. Still no retrieval or grounding.",
        "architecture": "Same direct request-response pattern. Prompt engineering alone cannot prevent hallucinations.",
        "known_limitations": "Model confidently fabricates specific facts (prices, specs, policies) that sound plausible but are wrong.",
    },
    "v3": {
        "prompt_strategy": "RAG prompt with context injection. System prompt instructs model to use ONLY provided context.",
        "architecture": "RAG pipeline: question → ChromaDB similarity search → retrieve relevant docs → inject into prompt → Claude API call.",
        "known_limitations": 'Dependent on knowledge base completeness. Questions outside KB scope get "I don\'t have information" response.',
    },
}


def get_failure_modes(version: str) -> list:
    """Get failure modes for a specific version."""
    return FAILURE_MODES.get(version, [])


def get_architecture_context(version: str) -> dict:
    """Get architecture context for a specific version."""
    return ARCHITECTURE_CONTEXT.get(version, {})


VERSIONS = [
    {
        "id": "v1",
        "name": "Version 1",
        "subtitle": "Verbose",
        "color": "warning",
        "problem": "Responses are too long (~300 words instead of ~80)",
        "fix": "Updated prompt to request concise 80-word responses",
        "prompt_change": 'Changed "at least 300 words" to "approximately 80 words"',
    },
    {
        "id": "v2",
        "name": "Version 2",
        "subtitle": "Hallucinating",
        "color": "error",
        "problem": "Model fabricates specific facts (prices, policies)",
        "fix": "Added RAG with Chroma to ground responses in actual data",
        "prompt_change": "Added context injection with retrieved documents",
    },
    {
        "id": "v3",
        "name": "Version 3",
        "subtitle": "Accurate",
        "color": "success",
        "problem": "N/A - This version passes all evals",
        "fix": "Production-ready with concise, accurate responses",
        "prompt_change": "Using V3_SYSTEM_PROMPT with RAG context",
    },
]


def get_iteration_summary() -> List[Dict]:
    """Get summary for each version"""
    summaries = []

    for version in VERSIONS:
        stats = get_trace_summary(version["id"])
        summaries.append({**version, "stats": stats})

    return summaries


def get_comparison_data() -> Dict:
    """Get data for side-by-side comparison"""
    return {
        "versions": VERSIONS,
        "metrics": [
            {
                "name": "Response Length",
                "v1": "~300 words",
                "v2": "~80 words",
                "v3": "~80 words",
                "target": "~80 words",
            },
            {
                "name": "Factual Accuracy",
                "v1": "N/A (too verbose)",
                "v2": "Low (hallucinations)",
                "v3": "High (grounded)",
                "target": "High",
            },
            {
                "name": "Sources Cited",
                "v1": "None",
                "v2": "None",
                "v3": "Yes",
                "target": "Yes",
            },
            {
                "name": "Eval Pass Rate",
                "v1": "0%",
                "v2": "33%",
                "v3": "100%",
                "target": "100%",
            },
        ],
        "key_lessons": [
            {
                "title": "Prompt Engineering Matters",
                "description": "V1 to V2 shows how a simple prompt change can fix behavioral issues like response length.",
            },
            {
                "title": "LLMs Hallucinate Without Grounding",
                "description": "V2 demonstrates that LLMs will confidently make up facts. RAG provides the grounding needed for accuracy.",
            },
            {
                "title": "Evals Guide Iteration",
                "description": "Each version was improved based on eval failures. Evals are your acceptance tests for AI behavior.",
            },
        ],
    }


def get_version_diff(from_version: str, to_version: str) -> Dict:
    """Get the differences between two versions"""
    version_map = {v["id"]: v for v in VERSIONS}

    from_v = version_map.get(from_version)
    to_v = version_map.get(to_version)

    if not from_v or not to_v:
        return {}

    return {
        "from": from_v,
        "to": to_v,
        "problem_fixed": from_v["problem"],
        "solution": to_v["fix"] if to_v["fix"] != from_v["fix"] else "Same approach",
        "prompt_diff": to_v["prompt_change"],
    }
