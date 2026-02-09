"""Trace Inspector - View AI interaction traces with annotations"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict

# Get the base directory
BASE_DIR = Path(__file__).parent.parent
TRACES_DIR = BASE_DIR / "data" / "traces"

# Axial codes: single source of truth for annotation category labels.
# Each trace annotation's `type` field maps to one of these codes.
# `text` field = open code (free-text observation); `type` = axial code.
AXIAL_CODES = {
    "length_violation": {
        "label": "Length Violation",
        "description": "Response length outside target range",
        "category": "format",
        "severity": "warning",
    },
    "prompt_issue": {
        "label": "Prompt Design Issue",
        "description": "System prompt causes undesirable behavior",
        "category": "design",
        "severity": "info",
    },
    "hallucination": {
        "label": "Factual Hallucination",
        "description": "Model fabricates facts not in source data",
        "category": "accuracy",
        "severity": "error",
    },
    "missing_source": {
        "label": "Missing Source Attribution",
        "description": "Response lacks KB citations",
        "category": "grounding",
        "severity": "warning",
    },
    "accurate_answer": {
        "label": "Verified Accurate",
        "description": "Information confirmed against KB",
        "category": "accuracy",
        "severity": "success",
    },
    "correct_retrieval": {
        "label": "Correct Retrieval",
        "description": "RAG retrieved the relevant document",
        "category": "grounding",
        "severity": "success",
    },
}


def get_annotation_summary() -> Dict:
    """Count each axial code per version across all traces.

    Returns:
        {"v1": {"length_violation": 20, ...}, "v2": {...}, "v3": {...}}
    """
    summary: Dict[str, Dict[str, int]] = {}
    for version in ["v1", "v2", "v3"]:
        trace_file = TRACES_DIR / f"{version}_traces.json"
        counts: Dict[str, int] = {code: 0 for code in AXIAL_CODES}
        if trace_file.exists():
            try:
                traces = json.loads(trace_file.read_text())
                for trace in traces:
                    for ann in trace.get("annotations", []):
                        ann_type = ann.get("type", "")
                        if ann_type in counts:
                            counts[ann_type] += 1
            except (json.JSONDecodeError, KeyError):
                pass
        summary[version] = counts
    return summary


@dataclass
class Annotation:
    """Annotation on a trace response"""

    type: str  # length_violation, hallucination, missing_source, correct_retrieval, accurate_answer, prompt_issue
    severity: str  # error, warning, success, info
    text: str  # Human-readable explanation
    span_start: Optional[int] = None  # Character position in response
    span_end: Optional[int] = None


@dataclass
class Trace:
    """A single AI interaction trace"""

    id: str
    version: str  # v1, v2, v3
    question: str
    prompt: str
    response: str
    latency_ms: int
    tokens: Dict
    sources: List[Dict] = field(default_factory=list)
    annotations: List[Dict] = field(default_factory=list)


def get_traces_by_version(version: str) -> List[Dict]:
    """Get list of traces for a given version"""
    trace_file = TRACES_DIR / f"{version}_traces.json"

    if not trace_file.exists():
        return []

    try:
        traces = json.loads(trace_file.read_text())
        return [
            {
                "id": t["id"],
                "question": (
                    t["question"][:50] + "..."
                    if len(t["question"]) > 50
                    else t["question"]
                ),
                "has_annotations": len(t.get("annotations", [])) > 0,
            }
            for t in traces
        ]
    except (json.JSONDecodeError, KeyError):
        return []


def get_trace_detail(trace_id: str) -> Optional[Dict]:
    """Get full trace details including annotations"""
    # Determine version from trace ID
    for version in ["v1", "v2", "v3"]:
        trace_file = TRACES_DIR / f"{version}_traces.json"
        if not trace_file.exists():
            continue

        try:
            traces = json.loads(trace_file.read_text())
            for trace in traces:
                if trace["id"] == trace_id:
                    return trace
        except (json.JSONDecodeError, KeyError):
            continue

    return None


def render_annotated_response(response: str, annotations: List[Dict]) -> str:
    """Render response text with annotation highlighting"""
    if not annotations:
        return response

    # Sort annotations by span_start (reverse order for safe insertion)
    sorted_anns = sorted(
        [a for a in annotations if a.get("span_start") is not None],
        key=lambda x: x["span_start"],
        reverse=True,
    )

    result = response

    for i, ann in enumerate(sorted_anns):
        start = ann["span_start"]
        end = ann.get("span_end", start + 20)

        # Create annotated span
        span_text = result[start:end]
        marker = (
            len(sorted_anns) - i
        )  # Reverse numbering since we're inserting backwards
        highlighted = f'<span class="ann ann--{ann["severity"]}" title="{ann["text"]}">{span_text}<sup class="ann__marker">{marker}</sup></span>'

        result = result[:start] + highlighted + result[end:]

    return result


def get_trace_summary(version: str) -> Dict:
    """Get summary statistics for traces of a version"""
    trace_file = TRACES_DIR / f"{version}_traces.json"

    if not trace_file.exists():
        return {
            "count": 0,
            "avg_latency": 0,
            "avg_tokens": 0,
            "error_count": 0,
            "warning_count": 0,
            "success_count": 0,
        }

    try:
        traces = json.loads(trace_file.read_text())

        total_latency = sum(t.get("latency_ms", 0) for t in traces)
        total_tokens = sum(t.get("tokens", {}).get("completion", 0) for t in traces)

        error_count = 0
        warning_count = 0
        success_count = 0

        for trace in traces:
            for ann in trace.get("annotations", []):
                if ann["severity"] == "error":
                    error_count += 1
                elif ann["severity"] == "warning":
                    warning_count += 1
                elif ann["severity"] == "success":
                    success_count += 1

        count = len(traces)
        return {
            "count": count,
            "avg_latency": total_latency // count if count else 0,
            "avg_tokens": total_tokens // count if count else 0,
            "error_count": error_count,
            "warning_count": warning_count,
            "success_count": success_count,
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "count": 0,
            "avg_latency": 0,
            "avg_tokens": 0,
            "error_count": 0,
            "warning_count": 0,
            "success_count": 0,
        }
