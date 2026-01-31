"""Go/No-Go rules engine for automated deployment decisions"""

from typing import Tuple, List
from .models import TestSummaryReport, GoNoGoDecision, TestType


# Default rules configuration
DEFAULT_RULES = {
    "blocking_conditions": [
        {
            "type": "test_type_all_fail",
            "test_type": "security",
            "message": "Security tests must all pass"
        },
        {
            "type": "test_type_all_fail",
            "test_type": "unit",
            "message": "Unit tests must all pass"
        },
        {
            "type": "eval_metric_below",
            "metric": "accuracy",
            "threshold": 0.85,
            "message": "Eval accuracy below 85%"
        },
        {
            "type": "unresolved_failure_mode",
            "severity": "critical",
            "message": "Critical failure mode unresolved"
        }
    ],
    "warning_conditions": [
        {
            "type": "eval_metric_below",
            "metric": "grounding_score",
            "threshold": 0.90,
            "message": "Grounding score below 90%"
        },
        {
            "type": "test_failure_rate",
            "test_type": "performance",
            "threshold": 0.05,
            "message": "Performance test failure rate above 5%"
        }
    ],
    "required_coverage": {
        "requirements": 0.95,
        "code": 0.80
    },
    "eval_requirements": {
        "min_iterations_documented": 1,
        "latest_iteration_must_pass": True
    }
}


class GoNoGoEvaluator:
    """Evaluates TSR against rules to determine go/no-go decision"""

    def __init__(self, rules: dict = None):
        """Initialize evaluator with rules configuration

        Args:
            rules: Optional custom rules dict, defaults to DEFAULT_RULES
        """
        self.rules = rules or DEFAULT_RULES

    def evaluate(self, tsr: TestSummaryReport) -> Tuple[GoNoGoDecision, str, List[str], List[str]]:
        """Evaluate TSR and return deployment decision

        Args:
            tsr: Test Summary Report to evaluate

        Returns:
            Tuple of (decision, reason, blocking_issues, warnings)
        """
        blocking = []
        warnings = []

        # Check test results against blocking conditions
        blocking.extend(self._check_test_results(tsr))

        # Check eval metrics
        blocking.extend(self._check_eval_metrics(tsr))
        warnings.extend(self._check_eval_warnings(tsr))

        # Check failure modes
        blocking.extend(self._check_failure_modes(tsr))

        # Check requirement coverage
        blocking.extend(self._check_requirement_coverage(tsr))

        # Check eval iteration requirements
        blocking.extend(self._check_eval_requirements(tsr))

        # Determine decision
        if blocking:
            decision = GoNoGoDecision.NO_GO
            reason = f"{len(blocking)} blocking issue(s) found"
        elif tsr.manual_approval_required:
            decision = GoNoGoDecision.PENDING_REVIEW
            reason = "Manual approval required"
        else:
            decision = GoNoGoDecision.GO
            reason = "All checks passed"

        return decision, reason, blocking, warnings

    def _check_test_results(self, tsr: TestSummaryReport) -> List[str]:
        """Check test results against blocking conditions"""
        blocking = []

        for result in tsr.test_results:
            # Security and unit tests must all pass
            if result.test_type.value in ['security', 'unit'] and result.failed > 0:
                blocking.append(
                    f"{result.test_type.value.upper()}: {result.failed} test(s) failed"
                )

            # Check for zero tests (potential CI issue)
            if result.total == 0:
                blocking.append(
                    f"{result.test_type.value.upper()}: No tests found or executed"
                )

        return blocking

    def _check_eval_metrics(self, tsr: TestSummaryReport) -> List[str]:
        """Check eval metrics against blocking thresholds"""
        blocking = []

        if not tsr.eval_iterations:
            return blocking

        latest = tsr.eval_iterations[-1]

        # Check accuracy threshold
        accuracy = latest.metrics.get('accuracy', 0)
        if accuracy < self.rules['blocking_conditions'][2]['threshold']:
            blocking.append(
                f"Eval accuracy {accuracy:.1%} below threshold "
                f"{self.rules['blocking_conditions'][2]['threshold']:.1%}"
            )

        # Check if latest iteration passed
        if latest.outcome not in ['passed', 'improved']:
            blocking.append(
                f"Latest eval iteration ({latest.version_name}) did not pass: {latest.outcome}"
            )

        return blocking

    def _check_eval_warnings(self, tsr: TestSummaryReport) -> List[str]:
        """Check eval metrics against warning thresholds"""
        warnings = []

        if not tsr.eval_iterations:
            return warnings

        latest = tsr.eval_iterations[-1]

        # Check grounding score
        grounding = latest.metrics.get('grounding_score', 1.0)
        grounding_threshold = self.rules['warning_conditions'][0]['threshold']
        if grounding < grounding_threshold:
            warnings.append(
                f"Grounding score {grounding:.1%} below recommended {grounding_threshold:.1%}"
            )

        return warnings

    def _check_failure_modes(self, tsr: TestSummaryReport) -> List[str]:
        """Check for unresolved critical failure modes"""
        blocking = []

        for iteration in tsr.eval_iterations:
            for fm in iteration.failure_modes:
                if fm.severity == 'critical' and fm.resolution_status == 'open':
                    blocking.append(
                        f"Unresolved critical failure mode: {fm.name} ({fm.category})"
                    )

        return blocking

    def _check_requirement_coverage(self, tsr: TestSummaryReport) -> List[str]:
        """Check requirement coverage against threshold"""
        blocking = []

        if not tsr.requirement_coverage:
            return blocking

        verified = sum(
            1 for r in tsr.requirement_coverage
            if r.verification_status == 'verified'
        )
        total = len(tsr.requirement_coverage)
        coverage_rate = verified / total if total > 0 else 0

        required_coverage = self.rules['required_coverage']['requirements']
        if coverage_rate < required_coverage:
            blocking.append(
                f"Requirement coverage {coverage_rate:.1%} below threshold "
                f"{required_coverage:.1%} ({verified}/{total} verified)"
            )

        return blocking

    def _check_eval_requirements(self, tsr: TestSummaryReport) -> List[str]:
        """Check eval iteration requirements"""
        blocking = []

        min_iterations = self.rules['eval_requirements']['min_iterations_documented']
        if len(tsr.eval_iterations) < min_iterations:
            blocking.append(
                f"Only {len(tsr.eval_iterations)} eval iteration(s) documented, "
                f"minimum {min_iterations} required"
            )

        return blocking

    def apply_decision(self, tsr: TestSummaryReport) -> None:
        """Apply go/no-go decision to TSR in-place

        Args:
            tsr: Test Summary Report to update
        """
        decision, reason, blocking, warnings = self.evaluate(tsr)

        tsr.go_no_go_decision = decision
        tsr.decision_reason = reason
        tsr.blocking_issues = blocking
        tsr.warnings = warnings

        # Update overall status
        if decision == GoNoGoDecision.NO_GO:
            tsr.overall_status = "failed"
        elif decision == GoNoGoDecision.PENDING_REVIEW:
            tsr.overall_status = "pending_review"
        else:
            tsr.overall_status = "passed"
