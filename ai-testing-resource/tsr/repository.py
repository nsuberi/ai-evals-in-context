"""Repository layer for TSR database operations"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from .models import (
    TestSummaryReport, VersionManifest, TestTypeResult,
    EvalIterationSummary, RequirementCoverage, GoNoGoDecision
)
from .database import (
    TSRModel, TSRTestResult, TSREvalIteration, TSRRequirementCoverage
)


class TSRRepository:
    """Repository for TSR database operations"""

    def __init__(self, session: Session):
        """Initialize repository with database session

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def save(self, tsr: TestSummaryReport) -> str:
        """Save or update a TSR

        Args:
            tsr: Test Summary Report to save

        Returns:
            TSR ID
        """
        # Check if TSR already exists
        existing = self.session.query(TSRModel).filter_by(id=tsr.id).first()

        if existing:
            # Update existing TSR
            self._update_tsr_model(existing, tsr)
        else:
            # Create new TSR
            tsr_model = self._tsr_to_model(tsr)
            self.session.add(tsr_model)

        self.session.commit()
        return tsr.id

    def get_by_id(self, tsr_id: str) -> Optional[TestSummaryReport]:
        """Get TSR by ID

        Args:
            tsr_id: TSR ID

        Returns:
            TestSummaryReport or None if not found
        """
        tsr_model = self.session.query(TSRModel).filter_by(id=tsr_id).first()
        if not tsr_model:
            return None
        return self._model_to_tsr(tsr_model)

    def get_latest(self, environment: Optional[str] = None) -> Optional[TestSummaryReport]:
        """Get most recent TSR

        Args:
            environment: Optional environment filter

        Returns:
            TestSummaryReport or None
        """
        query = self.session.query(TSRModel)
        if environment:
            query = query.filter_by(environment=environment)

        tsr_model = query.order_by(desc(TSRModel.created_at)).first()
        if not tsr_model:
            return None
        return self._model_to_tsr(tsr_model)

    def query(
        self,
        environment: Optional[str] = None,
        decision: Optional[str] = None,
        codebase_sha: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TestSummaryReport]:
        """Query TSRs with filters

        Args:
            environment: Filter by environment
            decision: Filter by go/no-go decision
            codebase_sha: Filter by codebase SHA
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            List of TestSummaryReports
        """
        query = self.session.query(TSRModel)

        if environment:
            query = query.filter_by(environment=environment)
        if decision:
            query = query.filter_by(go_no_go_decision=decision)
        if codebase_sha:
            query = query.filter_by(codebase_sha=codebase_sha)

        query = query.order_by(desc(TSRModel.created_at))
        query = query.limit(limit).offset(offset)

        return [self._model_to_tsr(model) for model in query.all()]

    def count(self, environment: Optional[str] = None, decision: Optional[str] = None) -> int:
        """Count TSRs matching filters

        Args:
            environment: Filter by environment
            decision: Filter by go/no-go decision

        Returns:
            Count of matching TSRs
        """
        query = self.session.query(TSRModel)

        if environment:
            query = query.filter_by(environment=environment)
        if decision:
            query = query.filter_by(go_no_go_decision=decision)

        return query.count()

    def delete(self, tsr_id: str) -> bool:
        """Delete a TSR

        Args:
            tsr_id: TSR ID to delete

        Returns:
            True if deleted, False if not found
        """
        tsr_model = self.session.query(TSRModel).filter_by(id=tsr_id).first()
        if not tsr_model:
            return False

        self.session.delete(tsr_model)
        self.session.commit()
        return True

    def _tsr_to_model(self, tsr: TestSummaryReport) -> TSRModel:
        """Convert TSR dataclass to database model"""
        tsr_model = TSRModel(
            id=tsr.id,
            created_at=tsr.created_at,
            triggered_by=tsr.triggered_by,
            environment=tsr.environment,
            overall_status=tsr.overall_status,
            go_no_go_decision=tsr.go_no_go_decision.value,
            decision_reason=tsr.decision_reason,
            blocking_issues=tsr.blocking_issues,
            warnings=tsr.warnings,
            manual_approval_required=tsr.manual_approval_required,
            approved_by=tsr.approved_by,
            approved_at=tsr.approved_at,
        )

        # Version manifest
        if tsr.versions:
            tsr_model.codebase_sha = tsr.versions.codebase_sha
            tsr_model.codebase_branch = tsr.versions.codebase_branch
            tsr_model.codebase_repo = tsr.versions.codebase_repo
            tsr_model.testbase_sha = tsr.versions.testbase_sha
            tsr_model.prompts_sha = tsr.versions.prompts_sha
            tsr_model.prompts_version = tsr.versions.prompts_version

        # Test results
        for result in tsr.test_results:
            tsr_model.test_results.append(TSRTestResult(
                test_type=result.test_type.value,
                total=result.total,
                passed=result.passed,
                failed=result.failed,
                skipped=result.skipped,
                duration_ms=result.duration_ms,
                failure_details=result.failure_details,
            ))

        # Eval iterations
        for iteration in tsr.eval_iterations:
            tsr_model.eval_iterations.append(TSREvalIteration(
                iteration=iteration.iteration,
                version_name=iteration.version_name,
                prompt_version=iteration.prompt_version,
                outcome=iteration.outcome,
                metrics=iteration.metrics,
                failure_modes=[fm.to_dict() for fm in iteration.failure_modes],
                fixes_applied=iteration.fixes_applied,
            ))

        # Requirement coverage
        for coverage in tsr.requirement_coverage:
            tsr_model.requirement_coverage.append(TSRRequirementCoverage(
                requirement_id=coverage.requirement_id,
                requirement_text=coverage.requirement_text,
                test_ids=coverage.test_ids,
                coverage_status=coverage.coverage_status,
                verification_status=coverage.verification_status,
            ))

        return tsr_model

    def _model_to_tsr(self, model: TSRModel) -> TestSummaryReport:
        """Convert database model to TSR dataclass"""
        from .models import FailureMode

        # Version manifest
        versions = VersionManifest(
            codebase_sha=model.codebase_sha,
            codebase_branch=model.codebase_branch,
            codebase_repo=model.codebase_repo,
            testbase_sha=model.testbase_sha,
            prompts_sha=model.prompts_sha,
            prompts_version=model.prompts_version,
        ) if model.codebase_sha else None

        # Test results
        test_results = []
        for result in model.test_results:
            from .models import TestType
            test_results.append(TestTypeResult(
                test_type=TestType(result.test_type),
                total=result.total,
                passed=result.passed,
                failed=result.failed,
                skipped=result.skipped,
                duration_ms=result.duration_ms,
                failure_details=result.failure_details or [],
            ))

        # Eval iterations
        eval_iterations = []
        for iteration in model.eval_iterations:
            failure_modes = [
                FailureMode.from_dict(fm) for fm in (iteration.failure_modes or [])
            ]
            eval_iterations.append(EvalIterationSummary(
                iteration=iteration.iteration,
                version_name=iteration.version_name,
                prompt_version=iteration.prompt_version,
                outcome=iteration.outcome,
                metrics=iteration.metrics,
                failure_modes=failure_modes,
                fixes_applied=iteration.fixes_applied or [],
            ))

        # Requirement coverage
        requirement_coverage = []
        for coverage in model.requirement_coverage:
            requirement_coverage.append(RequirementCoverage(
                requirement_id=coverage.requirement_id,
                requirement_text=coverage.requirement_text,
                test_ids=coverage.test_ids,
                coverage_status=coverage.coverage_status,
                verification_status=coverage.verification_status,
            ))

        return TestSummaryReport(
            id=str(model.id),
            created_at=model.created_at,
            triggered_by=model.triggered_by,
            environment=model.environment,
            versions=versions,
            test_results=test_results,
            eval_iterations=eval_iterations,
            requirement_coverage=requirement_coverage,
            overall_status=model.overall_status,
            go_no_go_decision=GoNoGoDecision(model.go_no_go_decision),
            decision_reason=model.decision_reason,
            blocking_issues=model.blocking_issues or [],
            warnings=model.warnings or [],
            manual_approval_required=model.manual_approval_required,
            approved_by=model.approved_by,
            approved_at=model.approved_at,
        )

    def _update_tsr_model(self, model: TSRModel, tsr: TestSummaryReport):
        """Update existing TSR model with new data"""
        model.overall_status = tsr.overall_status
        model.go_no_go_decision = tsr.go_no_go_decision.value
        model.decision_reason = tsr.decision_reason
        model.blocking_issues = tsr.blocking_issues
        model.warnings = tsr.warnings
        model.manual_approval_required = tsr.manual_approval_required
        model.approved_by = tsr.approved_by
        model.approved_at = tsr.approved_at

        # Clear and rebuild relationships
        model.test_results.clear()
        model.eval_iterations.clear()
        model.requirement_coverage.clear()

        # Rebuild test results
        for result in tsr.test_results:
            model.test_results.append(TSRTestResult(
                test_type=result.test_type.value,
                total=result.total,
                passed=result.passed,
                failed=result.failed,
                skipped=result.skipped,
                duration_ms=result.duration_ms,
                failure_details=result.failure_details,
            ))

        # Rebuild eval iterations
        for iteration in tsr.eval_iterations:
            model.eval_iterations.append(TSREvalIteration(
                iteration=iteration.iteration,
                version_name=iteration.version_name,
                prompt_version=iteration.prompt_version,
                outcome=iteration.outcome,
                metrics=iteration.metrics,
                failure_modes=[fm.to_dict() for fm in iteration.failure_modes],
                fixes_applied=iteration.fixes_applied,
            ))

        # Rebuild requirement coverage
        for coverage in tsr.requirement_coverage:
            model.requirement_coverage.append(TSRRequirementCoverage(
                requirement_id=coverage.requirement_id,
                requirement_text=coverage.requirement_text,
                test_ids=coverage.test_ids,
                coverage_status=coverage.coverage_status,
                verification_status=coverage.verification_status,
            ))
