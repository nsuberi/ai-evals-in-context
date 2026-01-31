#!/usr/bin/env python3
"""
Initialize monitoring baselines from V3 traces (production-ready performance)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from monitoring.models import ProductionTrace, AnomalyThresholds
from monitoring.anomaly import AnomalyDetector
from monitoring.metrics import MetricsAggregator


def load_traces_from_file(trace_file: Path) -> list:
    """Load production traces from JSON file"""
    with open(trace_file, 'r') as f:
        data = json.load(f)

    traces = []
    for item in data:
        trace = ProductionTrace(
            id=item['id'],
            timestamp=datetime.fromisoformat(item['timestamp']),
            question=item['question'],
            response=item['response'],
            latency_ms=item['latency_ms'],
            prompt_tokens=item.get('prompt_tokens', 0),
            completion_tokens=item.get('completion_tokens', 0),
            model_version=item.get('model_version', 'unknown'),
            prompt_version=item.get('prompt_version', 'unknown'),
            sources=item.get('sources', []),
            user_feedback=item.get('user_feedback'),
            detected_category=item.get('detected_category'),
            anomaly_flags=item.get('anomaly_flags', [])
        )
        traces.append(trace)

    return traces


def calculate_baselines():
    """Calculate and save monitoring baselines"""
    print("\n=== Initializing Monitoring Baselines ===")

    # Load V3 traces (production-ready performance)
    v3_traces_file = Path(__file__).parent.parent / 'data' / 'traces' / 'v3_traces.json'

    if not v3_traces_file.exists():
        print(f"⚠ V3 traces file not found: {v3_traces_file}")
        print("  Creating default baselines from recommended values...")

        # Use recommended defaults from documentation
        baselines = {
            'latency_p95': 1850,
            'satisfaction_rate': 1.0,
            'source': 'default_recommendations',
            'timestamp': datetime.utcnow().isoformat()
        }

    else:
        print(f"Loading traces from: {v3_traces_file}")
        traces = load_traces_from_file(v3_traces_file)
        print(f"  Loaded {len(traces)} traces")

        # Calculate metrics using aggregator
        aggregator = MetricsAggregator()
        for trace in traces:
            aggregator.add_trace(trace)

        # Get metrics summary for entire period
        metrics = aggregator.get_summary(window_minutes=24 * 60)  # 24 hours

        baselines = {
            'latency_p50': metrics.latency_p50,
            'latency_p95': metrics.latency_p95,
            'latency_p99': metrics.latency_p99,
            'satisfaction_rate': metrics.satisfaction_rate,
            'avg_prompt_tokens': metrics.avg_prompt_tokens,
            'avg_completion_tokens': metrics.avg_completion_tokens,
            'trace_count': metrics.trace_count,
            'source': 'v3_traces',
            'timestamp': datetime.utcnow().isoformat()
        }

        print(f"\nCalculated baselines:")
        print(f"  P50 Latency: {baselines['latency_p50']:.0f}ms")
        print(f"  P95 Latency: {baselines['latency_p95']:.0f}ms")
        print(f"  P99 Latency: {baselines['latency_p99']:.0f}ms")
        print(f"  Satisfaction: {baselines['satisfaction_rate']:.1%}")
        print(f"  Avg Prompt Tokens: {baselines['avg_prompt_tokens']:.0f}")
        print(f"  Avg Completion Tokens: {baselines['avg_completion_tokens']:.0f}")

    # Save baselines to config file
    baselines_file = Path(__file__).parent.parent / 'config' / 'monitoring_baselines.json'
    baselines_file.parent.mkdir(exist_ok=True)

    with open(baselines_file, 'w') as f:
        json.dump(baselines, f, indent=2)

    print(f"\n✓ Baselines saved to: {baselines_file}")

    # Initialize detector with baselines
    detector = AnomalyDetector(thresholds=AnomalyThresholds(
        latency_p95_multiplier=1.5,
        error_rate_threshold=0.05,
        satisfaction_drop_threshold=0.10,
        grounding_score_min=0.85,
        window_minutes=15
    ))

    detector.set_baseline(
        latency_p95=baselines['latency_p95'],
        satisfaction=baselines['satisfaction_rate']
    )

    print("\n✓ Anomaly detector initialized with baselines")
    print(f"  Latency alert threshold: {baselines['latency_p95'] * 1.5:.0f}ms")
    print(f"  Satisfaction alert threshold: {baselines['satisfaction_rate'] - 0.10:.1%}")

    return baselines


if __name__ == '__main__':
    calculate_baselines()
