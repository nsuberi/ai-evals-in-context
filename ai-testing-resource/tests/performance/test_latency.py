"""
Performance Test: Response Latency

Tests that responses are generated within acceptable time limits.
Important for user experience.
"""
import pytest
import time
import os
from app.ai_service import ask_v1, ask_v2, ask_v3

# Latency thresholds in milliseconds
THRESHOLD_P50 = 2000   # 50th percentile: 2 seconds
THRESHOLD_P95 = 5000   # 95th percentile: 5 seconds
THRESHOLD_MAX = 10000  # Maximum: 10 seconds

# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)


class TestLatency:
    """Test suite for response latency"""

    @pytest.fixture(autouse=True)
    def setup(self, knowledge_base):
        pass

    def measure_latency(self, ask_func, question: str) -> int:
        """Measure latency of a single request in ms"""
        start = time.time()
        result = ask_func(question)
        elapsed = (time.time() - start) * 1000
        return int(elapsed)

    def test_v1_latency_acceptable(self):
        """V1 response should complete within threshold"""
        latency = self.measure_latency(ask_v1, "What is your return policy?")

        # V1 generates verbose 300+ word responses, allow more time
        verbose_threshold = THRESHOLD_MAX * 1.2

        assert latency < verbose_threshold, \
            f"V1 latency {latency}ms exceeds maximum {verbose_threshold}ms"

    def test_v2_latency_acceptable(self):
        """V2 response should complete within threshold"""
        latency = self.measure_latency(ask_v2, "What is your return policy?")

        assert latency < THRESHOLD_MAX, \
            f"V2 latency {latency}ms exceeds maximum {THRESHOLD_MAX}ms"

    def test_v3_latency_acceptable(self):
        """V3 (RAG) response should complete within threshold"""
        latency = self.measure_latency(ask_v3, "What is your return policy?")

        # V3 has additional retrieval step, allow more time
        rag_threshold = THRESHOLD_MAX * 1.5

        assert latency < rag_threshold, \
            f"V3 latency {latency}ms exceeds maximum {rag_threshold}ms"

    def test_latency_consistency(self):
        """Multiple requests should have consistent latency"""
        latencies = []
        question = "How much does shipping cost?"

        for _ in range(3):
            latency = self.measure_latency(ask_v3, question)
            latencies.append(latency)

        avg_latency = sum(latencies) / len(latencies)
        max_variance = max(latencies) - min(latencies)

        # Variance should be less than 100% of average (allows for network jitter)
        assert max_variance < avg_latency * 1.0, \
            f"High latency variance: {max_variance}ms (avg: {avg_latency}ms)"
