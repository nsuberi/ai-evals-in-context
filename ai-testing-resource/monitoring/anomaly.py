"""Anomaly detection for production metrics"""

from typing import Optional, List
import uuid
from datetime import datetime

from .models import AnomalyThresholds, Anomaly, MetricsSummary


class AnomalyDetector:
    """Detects anomalies in production metrics"""

    def __init__(self, thresholds: Optional[AnomalyThresholds] = None):
        """Initialize detector with thresholds

        Args:
            thresholds: Optional custom thresholds, defaults to AnomalyThresholds()
        """
        self.thresholds = thresholds or AnomalyThresholds()
        self.baseline_latency_p95: Optional[float] = None
        self.baseline_satisfaction: Optional[float] = None

    def set_baseline(self, latency_p95: float, satisfaction: float):
        """Set baseline metrics from stable period

        Args:
            latency_p95: Baseline P95 latency in ms
            satisfaction: Baseline satisfaction rate (0-1)
        """
        self.baseline_latency_p95 = latency_p95
        self.baseline_satisfaction = satisfaction

    def check_anomalies(self, metrics: MetricsSummary) -> List[Anomaly]:
        """Check for anomalies in metrics summary

        Args:
            metrics: Current metrics to check

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Check latency anomaly
        latency_anomaly = self.check_latency_anomaly(metrics.latency_p95)
        if latency_anomaly:
            anomalies.append(latency_anomaly)

        # Check error rate anomaly
        error_rate = metrics.error_count / metrics.trace_count if metrics.trace_count > 0 else 0
        error_anomaly = self.check_error_rate_anomaly(error_rate)
        if error_anomaly:
            anomalies.append(error_anomaly)

        # Check satisfaction anomaly
        satisfaction_anomaly = self.check_satisfaction_anomaly(metrics.satisfaction_rate)
        if satisfaction_anomaly:
            anomalies.append(satisfaction_anomaly)

        return anomalies

    def check_latency_anomaly(self, current_p95: float) -> Optional[Anomaly]:
        """Check for latency anomaly

        Args:
            current_p95: Current P95 latency in ms

        Returns:
            Anomaly if detected, None otherwise
        """
        if not self.baseline_latency_p95:
            return None

        threshold = self.baseline_latency_p95 * self.thresholds.latency_p95_multiplier

        if current_p95 > threshold:
            severity = self._calculate_severity(
                current_p95,
                threshold,
                threshold * 1.2
            )

            return Anomaly(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                severity=severity,
                category='latency',
                description=f"P95 latency ({current_p95:.0f}ms) exceeds threshold ({threshold:.0f}ms)",
                current_value=current_p95,
                threshold_value=threshold
            )

        return None

    def check_error_rate_anomaly(self, current_rate: float) -> Optional[Anomaly]:
        """Check for error rate anomaly

        Args:
            current_rate: Current error rate (0-1)

        Returns:
            Anomaly if detected, None otherwise
        """
        threshold = self.thresholds.error_rate_threshold

        if current_rate > threshold:
            severity = self._calculate_severity(
                current_rate,
                threshold,
                threshold * 2
            )

            return Anomaly(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                severity=severity,
                category='error_rate',
                description=f"Error rate ({current_rate:.1%}) exceeds threshold ({threshold:.1%})",
                current_value=current_rate,
                threshold_value=threshold
            )

        return None

    def check_satisfaction_anomaly(self, current_rate: float) -> Optional[Anomaly]:
        """Check for satisfaction drop anomaly

        Args:
            current_rate: Current satisfaction rate (0-1)

        Returns:
            Anomaly if detected, None otherwise
        """
        if not self.baseline_satisfaction:
            return None

        threshold = self.baseline_satisfaction - self.thresholds.satisfaction_drop_threshold

        if current_rate < threshold:
            severity = self._calculate_severity(
                abs(current_rate - self.baseline_satisfaction),
                self.thresholds.satisfaction_drop_threshold,
                self.thresholds.satisfaction_drop_threshold * 2
            )

            return Anomaly(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                severity=severity,
                category='satisfaction',
                description=(
                    f"Satisfaction rate ({current_rate:.1%}) dropped below threshold "
                    f"({threshold:.1%}, baseline: {self.baseline_satisfaction:.1%})"
                ),
                current_value=current_rate,
                threshold_value=threshold
            )

        return None

    def _calculate_severity(
        self,
        value: float,
        warning_threshold: float,
        critical_threshold: float
    ) -> str:
        """Calculate severity based on how much threshold is exceeded

        Args:
            value: Current value
            warning_threshold: Warning level threshold
            critical_threshold: Critical level threshold

        Returns:
            Severity string: low, medium, high, or critical
        """
        if value >= critical_threshold:
            return 'critical'
        elif value >= warning_threshold * 1.5:
            return 'high'
        elif value >= warning_threshold * 1.2:
            return 'medium'
        else:
            return 'low'
