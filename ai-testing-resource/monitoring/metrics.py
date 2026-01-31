"""Metrics aggregation for production monitoring"""

from typing import List
from datetime import datetime, timedelta
import statistics

from .models import ProductionTrace, MetricsSummary


class MetricsAggregator:
    """Aggregates metrics from production traces"""

    def __init__(self):
        self.traces: List[ProductionTrace] = []

    def add_trace(self, trace: ProductionTrace):
        """Add a trace to the aggregator

        Args:
            trace: Production trace to add
        """
        self.traces.append(trace)

    def get_summary(
        self,
        window_minutes: int = 15,
        end_time: datetime = None
    ) -> MetricsSummary:
        """Get aggregated metrics summary for a time window

        Args:
            window_minutes: Size of the time window in minutes
            end_time: End time for the window (default: now)

        Returns:
            MetricsSummary
        """
        if end_time is None:
            end_time = datetime.utcnow()

        window_start = end_time - timedelta(minutes=window_minutes)

        # Filter traces in window
        window_traces = [
            t for t in self.traces
            if window_start <= t.timestamp <= end_time
        ]

        if not window_traces:
            return MetricsSummary(
                window_start=window_start,
                window_end=end_time,
                trace_count=0,
                error_count=0,
                latency_p50=0,
                latency_p95=0,
                latency_p99=0,
                satisfaction_rate=0,
                avg_prompt_tokens=0,
                avg_completion_tokens=0
            )

        # Calculate metrics
        latencies = [t.latency_ms for t in window_traces]
        latencies.sort()

        error_count = sum(1 for t in window_traces if t.anomaly_flags)

        # Satisfaction rate
        positive = sum(1 for t in window_traces if t.user_feedback == 'positive')
        negative = sum(1 for t in window_traces if t.user_feedback == 'negative')
        satisfaction_rate = positive / (positive + negative) if (positive + negative) > 0 else 0

        return MetricsSummary(
            window_start=window_start,
            window_end=end_time,
            trace_count=len(window_traces),
            error_count=error_count,
            latency_p50=self._percentile(latencies, 0.50),
            latency_p95=self._percentile(latencies, 0.95),
            latency_p99=self._percentile(latencies, 0.99),
            satisfaction_rate=satisfaction_rate,
            avg_prompt_tokens=sum(t.prompt_tokens for t in window_traces) / len(window_traces),
            avg_completion_tokens=sum(t.completion_tokens for t in window_traces) / len(window_traces)
        )

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile

        Args:
            values: Sorted list of values
            percentile: Percentile to calculate (0-1)

        Returns:
            Percentile value
        """
        if not values:
            return 0

        index = int(len(values) * percentile)
        return values[min(index, len(values) - 1)]

    def clear_old_traces(self, keep_hours: int = 24):
        """Remove traces older than specified hours

        Args:
            keep_hours: Number of hours to keep
        """
        cutoff = datetime.utcnow() - timedelta(hours=keep_hours)
        self.traces = [t for t in self.traces if t.timestamp >= cutoff]
