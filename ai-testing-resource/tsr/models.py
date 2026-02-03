"""TSR data models"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
import uuid


class GoNoGoDecision(Enum):
    """Deployment decision status"""
    GO = "go"
    NO_GO = "no_go"
    PENDING_REVIEW = "pending_review"


class TestType(Enum):
    """Types of tests in the test suite"""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    ACCEPTANCE = "acceptance"
    EVALS = "evals"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STEEL_THREAD = "steelthread"


@dataclass
class VersionManifest:
    """Tracks git commits for all versioned components"""
    codebase_sha: str
    codebase_branch: str
    codebase_repo: str
    testbase_sha: str
    prompts_sha: str
    prompts_version: Optional[str] = None  # Semantic version like "v2.1.0"

    def to_dict(self) -> dict:
        return {
            'codebase_sha': self.codebase_sha,
            'codebase_branch': self.codebase_branch,
            'codebase_repo': self.codebase_repo,
            'testbase_sha': self.testbase_sha,
            'prompts_sha': self.prompts_sha,
            'prompts_version': self.prompts_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'VersionManifest':
        return cls(**data)


@dataclass
class TestTypeResult:
    """Results for a single test type"""
    test_type: TestType
    total: int
    passed: int
    failed: int
    skipped: int
    duration_ms: int
    failure_details: List[dict] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as a percentage"""
        return self.passed / self.total if self.total > 0 else 1.0

    def to_dict(self) -> dict:
        return {
            'test_type': self.test_type.value,
            'total': self.total,
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'duration_ms': self.duration_ms,
            'pass_rate': self.pass_rate,
            'failure_details': self.failure_details,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TestTypeResult':
        data['test_type'] = TestType(data['test_type'])
        return cls(**data)


@dataclass
class FailureMode:
    """A discovered failure mode in AI behavior"""
    id: str
    name: str
    description: str
    severity: str  # critical, major, minor
    category: str  # accuracy, format, safety, performance, grounding
    discovered_in_iteration: int
    resolution_status: str = "open"  # open, fixed, wont_fix, accepted_risk

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'severity': self.severity,
            'category': self.category,
            'discovered_in_iteration': self.discovered_in_iteration,
            'resolution_status': self.resolution_status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FailureMode':
        return cls(**data)


@dataclass
class EvalIterationSummary:
    """Summary of a single eval iteration (e.g., V1, V2, V3)"""
    iteration: int
    version_name: str  # "V1 Verbose", "V2 No RAG", "V3 RAG"
    prompt_version: str
    outcome: str  # failed, improved, passed
    metrics: dict  # accuracy, avg_length, grounding_score, latency
    failure_modes: List[FailureMode] = field(default_factory=list)
    fixes_applied: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'iteration': self.iteration,
            'version_name': self.version_name,
            'prompt_version': self.prompt_version,
            'outcome': self.outcome,
            'metrics': self.metrics,
            'failure_modes': [fm.to_dict() for fm in self.failure_modes],
            'fixes_applied': self.fixes_applied,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EvalIterationSummary':
        data['failure_modes'] = [
            FailureMode.from_dict(fm) for fm in data.get('failure_modes', [])
        ]
        return cls(**data)


@dataclass
class RequirementCoverage:
    """Coverage status for a single requirement"""
    requirement_id: str
    requirement_text: str
    test_ids: List[str]
    coverage_status: str  # covered, partial, uncovered
    verification_status: str  # verified, failed, not_run

    def to_dict(self) -> dict:
        return {
            'requirement_id': self.requirement_id,
            'requirement_text': self.requirement_text,
            'test_ids': self.test_ids,
            'coverage_status': self.coverage_status,
            'verification_status': self.verification_status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RequirementCoverage':
        return cls(**data)


@dataclass
class TestSummaryReport:
    """Complete Test Summary Report"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    triggered_by: str = "manual"
    environment: str = "test"

    versions: Optional[VersionManifest] = None
    test_results: List[TestTypeResult] = field(default_factory=list)
    eval_iterations: List[EvalIterationSummary] = field(default_factory=list)
    requirement_coverage: List[RequirementCoverage] = field(default_factory=list)

    overall_status: str = "passed"
    go_no_go_decision: GoNoGoDecision = GoNoGoDecision.PENDING_REVIEW
    decision_reason: str = ""
    blocking_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    manual_approval_required: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'triggered_by': self.triggered_by,
            'environment': self.environment,
            'versions': self.versions.to_dict() if self.versions else None,
            'test_results': [tr.to_dict() for tr in self.test_results],
            'eval_iterations': [ei.to_dict() for ei in self.eval_iterations],
            'requirement_coverage': [rc.to_dict() for rc in self.requirement_coverage],
            'overall_status': self.overall_status,
            'go_no_go_decision': self.go_no_go_decision.value,
            'decision_reason': self.decision_reason,
            'blocking_issues': self.blocking_issues,
            'warnings': self.warnings,
            'manual_approval_required': self.manual_approval_required,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TestSummaryReport':
        """Create TSR from dictionary"""
        # Parse datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'approved_at' in data and isinstance(data['approved_at'], str):
            data['approved_at'] = datetime.fromisoformat(data['approved_at'])

        # Parse enum field
        if 'go_no_go_decision' in data and isinstance(data['go_no_go_decision'], str):
            data['go_no_go_decision'] = GoNoGoDecision(data['go_no_go_decision'])

        # Parse nested objects
        if 'versions' in data and data['versions']:
            data['versions'] = VersionManifest.from_dict(data['versions'])
        if 'test_results' in data:
            data['test_results'] = [
                TestTypeResult.from_dict(tr) for tr in data['test_results']
            ]
        if 'eval_iterations' in data:
            data['eval_iterations'] = [
                EvalIterationSummary.from_dict(ei) for ei in data['eval_iterations']
            ]
        if 'requirement_coverage' in data:
            data['requirement_coverage'] = [
                RequirementCoverage.from_dict(rc) for rc in data['requirement_coverage']
            ]

        return cls(**data)

    def get_total_tests(self) -> int:
        """Get total number of tests across all types"""
        return sum(tr.total for tr in self.test_results)

    def get_total_passed(self) -> int:
        """Get total number of passed tests"""
        return sum(tr.passed for tr in self.test_results)

    def get_total_failed(self) -> int:
        """Get total number of failed tests"""
        return sum(tr.failed for tr in self.test_results)

    def get_overall_pass_rate(self) -> float:
        """Get overall pass rate across all tests"""
        total = self.get_total_tests()
        return self.get_total_passed() / total if total > 0 else 1.0
