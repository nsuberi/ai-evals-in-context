"""Drift detection comparing production to eval baseline"""

from typing import Dict, Optional


def compare_to_baseline(production_metrics: dict, eval_baseline: dict) -> Dict[str, dict]:
    """Compare production behavior to eval baseline

    Args:
        production_metrics: Current production metrics
        eval_baseline: Baseline metrics from eval phase

    Returns:
        Dictionary of comparison results per metric
    """
    results = {}

    metrics_to_check = [
        'accuracy',
        'grounding_score',
        'avg_response_length',
        'latency_p95'
    ]

    for metric in metrics_to_check:
        prod_value = production_metrics.get(metric)
        baseline_value = eval_baseline.get(metric)

        if prod_value is not None and baseline_value is not None:
            diff_pct = (prod_value - baseline_value) / baseline_value * 100

            # Determine status based on drift magnitude
            if abs(diff_pct) < 10:
                status = 'ok'
            elif abs(diff_pct) < 20:
                status = 'warning'
            else:
                status = 'critical'

            # For some metrics, negative drift is worse than positive
            if metric in ['accuracy', 'grounding_score']:
                if diff_pct < -10:
                    status = 'warning'
                if diff_pct < -20:
                    status = 'critical'

            results[metric] = {
                'production': prod_value,
                'baseline': baseline_value,
                'diff_pct': diff_pct,
                'diff_absolute': prod_value - baseline_value,
                'status': status
            }

    return results


def calculate_drift_score(comparison_results: dict) -> float:
    """Calculate overall drift score from comparison results

    Args:
        comparison_results: Results from compare_to_baseline

    Returns:
        Drift score from 0 (no drift) to 1 (severe drift)
    """
    if not comparison_results:
        return 0.0

    status_weights = {
        'ok': 0.0,
        'warning': 0.5,
        'critical': 1.0
    }

    total_weight = 0.0
    count = 0

    for metric, result in comparison_results.items():
        status = result['status']
        weight = status_weights.get(status, 0.0)

        # Weight critical metrics more heavily
        if metric in ['accuracy', 'grounding_score']:
            weight *= 1.5

        total_weight += weight
        count += 1

    return min(total_weight / count, 1.0) if count > 0 else 0.0


def detect_drift_patterns(traces: list, window_size: int = 100) -> Dict[str, any]:
    """Detect drift patterns in recent traces

    Args:
        traces: List of recent production traces
        window_size: Number of traces to analyze

    Returns:
        Dictionary with drift pattern analysis
    """
    if len(traces) < window_size:
        return {'status': 'insufficient_data', 'trace_count': len(traces)}

    recent = traces[-window_size:]

    # Analyze latency trend
    latencies = [t.latency_ms for t in recent]
    avg_latency = sum(latencies) / len(latencies)
    latency_trend = _calculate_trend(latencies)

    # Analyze user feedback trend
    positive_feedback = sum(1 for t in recent if t.user_feedback == 'positive')
    negative_feedback = sum(1 for t in recent if t.user_feedback == 'negative')
    satisfaction_rate = positive_feedback / (positive_feedback + negative_feedback) if (positive_feedback + negative_feedback) > 0 else None

    # Analyze anomaly flags
    traces_with_anomalies = sum(1 for t in recent if t.anomaly_flags)
    anomaly_rate = traces_with_anomalies / len(recent)

    return {
        'status': 'ok',
        'trace_count': len(recent),
        'avg_latency': avg_latency,
        'latency_trend': latency_trend,
        'satisfaction_rate': satisfaction_rate,
        'anomaly_rate': anomaly_rate,
        'drift_detected': anomaly_rate > 0.05 or (latency_trend and latency_trend > 0.2)
    }


def _calculate_trend(values: list) -> Optional[float]:
    """Calculate simple linear trend

    Args:
        values: List of numeric values

    Returns:
        Slope of trend line, or None if insufficient data
    """
    if len(values) < 2:
        return None

    n = len(values)
    x_mean = n / 2
    y_mean = sum(values) / n

    numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    return numerator / denominator if denominator != 0 else 0.0
