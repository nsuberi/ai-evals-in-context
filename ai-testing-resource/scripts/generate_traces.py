#!/usr/bin/env python3
"""Generate real traces by calling the AI service."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ai_service import ask_v1, ask_v2, ask_v3, V1_SYSTEM_PROMPT, V2_SYSTEM_PROMPT, V3_SYSTEM_PROMPT

QUESTIONS = [
    "What is your return policy?",
    "How much does the Enterprise plan cost?",
    "What are the specs of Widget Pro X2?",
    "What shipping options do you offer?",
    "Do you offer a free trial?",
]

def generate_trace(version_func, version, question, index):
    result = version_func(question)
    return {
        "id": f"{version}-trace-{index:03d}",
        "version": version,
        "question": question,
        "prompt": {"v1": V1_SYSTEM_PROMPT, "v2": V2_SYSTEM_PROMPT, "v3": V3_SYSTEM_PROMPT[:200]}[version],
        "response": result["text"],
        "latency_ms": result["metadata"]["latency_ms"],
        "tokens": {
            "prompt": result["metadata"]["prompt_tokens"],
            "completion": result["metadata"]["completion_tokens"]
        },
        "sources": result.get("sources", []),
        "annotations": []
    }

def main():
    output_dir = Path("data/traces")

    for version, func in [("v1", ask_v1), ("v2", ask_v2), ("v3", ask_v3)]:
        print(f"Generating {version} traces...")
        traces = [generate_trace(func, version, q, i+1) for i, q in enumerate(QUESTIONS)]

        # Add version-specific annotations
        for t in traces:
            if version == "v1":
                wc = len(t["response"].split())
                t["annotations"].append({"type": "length_violation", "severity": "warning",
                    "text": f"Response is {wc} words", "span_start": None, "span_end": None})
            elif version == "v2":
                t["annotations"].append({"type": "missing_source", "severity": "warning",
                    "text": "No sources cited", "span_start": None, "span_end": None})
            elif version == "v3" and t["sources"]:
                t["annotations"].append({"type": "correct_retrieval", "severity": "success",
                    "text": f"Retrieved: {t['sources'][0]['title']}", "span_start": None, "span_end": None})

        with open(output_dir / f"{version}_traces.json", "w") as f:
            json.dump(traces, f, indent=2)
        print(f"  Saved {len(traces)} traces")

if __name__ == "__main__":
    main()
