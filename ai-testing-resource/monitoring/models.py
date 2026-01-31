"""Data models for production monitoring"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict


@dataclass
class ProductionTrace:
    """A single AI interaction trace from production"""
    id: str
    timestamp: datetime
    question: str
    response: str
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    model_version: str
    prompt_version: str
    sources: List[dict] = field(default_factory=list)
    user_feedback: Optional[str] = None  # "positive", "negative"
    detected_category: Optional[str] = None
    anomaly_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'question': self.question,
            'response': self.response,
            'latency_ms': self.latency_ms,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'model_version': self.model_version,
            'prompt_version': self.prompt_version,
            'sources': self.sources,
            'user_feedback': self.user_feedback,
            'detected_category': self.detected_category,
            'anomaly_flags': self.anomaly_flags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ProductionTrace':
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class AnomalyThresholds:
    """Configurable thresholds for anomaly detection"""
    latency_p95_multiplier: float = 1.5
    error_rate_threshold: float = 0.05
    satisfaction_drop_threshold: float = 0.10
    grounding_score_min: float = 0.85
    window_minutes: int = 15

    def to_dict(self) -> dict:
        return {
            'latency_p95_multiplier': self.latency_p95_multiplier,
            'error_rate_threshold': self.error_rate_threshold,
            'satisfaction_drop_threshold': self.satisfaction_drop_threshold,
            'grounding_score_min': self.grounding_score_min,
            'window_minutes': self.window_minutes,
        }


@dataclass
class MetricsSummary:
    """Aggregated metrics for a time window"""
    window_start: datetime
    window_end: datetime
    trace_count: int
    error_count: int
    latency_p50: float
    latency_p95: float
    latency_p99: float
    satisfaction_rate: float
    avg_prompt_tokens: float
    avg_completion_tokens: float

    def to_dict(self) -> dict:
        return {
            'window_start': self.window_start.isoformat(),
            'window_end': self.window_end.isoformat(),
            'trace_count': self.trace_count,
            'error_count': self.error_count,
            'error_rate': self.error_count / self.trace_count if self.trace_count > 0 else 0,
            'latency_p50': self.latency_p50,
            'latency_p95': self.latency_p95,
            'latency_p99': self.latency_p99,
            'satisfaction_rate': self.satisfaction_rate,
            'avg_prompt_tokens': self.avg_prompt_tokens,
            'avg_completion_tokens': self.avg_completion_tokens,
        }


@dataclass
class Anomaly:
    """Detected anomaly"""
    id: str
    timestamp: datetime
    severity: str  # low, medium, high, critical
    category: str  # latency, error_rate, satisfaction, grounding
    description: str
    current_value: float
    threshold_value: float
    affected_traces: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity,
            'category': self.category,
            'description': self.description,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'affected_traces': self.affected_traces,
        }
