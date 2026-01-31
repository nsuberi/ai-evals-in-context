#!/usr/bin/env python3
"""
Seed the TSR database with sample test data for development and testing
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tsr.models import (
    TestSummaryReport, VersionManifest, TestTypeResult, TestType,
    EvalIterationSummary, FailureMode, RequirementCoverage, GoNoGoDecision
)
from tsr.repository import TSRRepository
from tsr.rules import GoNoGoEvaluator
from config import TSR_DATABASE_URL


def create_sample_version_manifest(iteration: int) -> VersionManifest:
    """Create version manifest for iteration"""
    return VersionManifest(
        codebase_sha=f"abc123{iteration}" + "0" * 34,
        codebase_branch="main",
        codebase_repo="https://github.com/example/ai-testing-resource",
        testbase_sha=f"def456{iteration}" + "0" * 34,
        prompts_sha=f"ghi789{iteration}" + "0" * 34,
        prompts_version=f"v1.{iteration}.0"
    )


def create_sample_test_results(iteration: int) -> list:
    """Create sample test results with iteration-specific pass rates"""
    # V1: Some failures, V2: Better, V3: All pass
    failure_counts = {
        1: {'unit': 2, 'security': 1, 'evals': 5},
        2: {'unit': 0, 'security': 0, 'evals': 2},
        3: {'unit': 0, 'security': 0, 'evals': 0}
    }

    base_counts = {
        'unit': 45,
        'integration': 12,
        'e2e': 8,
        'acceptance': 6,
        'evals': 15,
        'security': 10,
        'performance': 5
    }

    results = []
    for test_type, total in base_counts.items():
        failed = failure_counts.get(iteration, {}).get(test_type, 0)
        passed = total - failed

        results.append(TestTypeResult(
            test_type=TestType(test_type),
            total=total,
            passed=passed,
            failed=failed,
            skipped=0,
            duration_ms=(total * 150) + (iteration * 100),
            failure_details=[]
        ))

    return results


def create_sample_eval_iterations(up_to_iteration: int) -> list:
    """Create eval iteration history"""
    iterations = []

    # V1: Verbose
    if up_to_iteration >= 1:
        iterations.append(EvalIterationSummary(
            iteration=1,
            version_name="V1 Verbose",
            prompt_version="v1.0",
            outcome="failed",
            metrics={
                "accuracy": 0.65,
                "avg_response_length": 320,
                "grounding_score": 0.0,
                "latency_p95": 2850
            },
            failure_modes=[
                FailureMode(
                    id=str(uuid.uuid4()),
                    name="Excessive verbosity",
                    description="Responses exceed 300 words vs 80-word target",
                    severity="major",
                    category="format",
                    discovered_in_iteration=1,
                    resolution_status="fixed"
                )
            ],
            fixes_applied=[]
        ))

    # V2: Concise but hallucinating
    if up_to_iteration >= 2:
        iterations.append(EvalIterationSummary(
            iteration=2,
            version_name="V2 No RAG",
            prompt_version="v2.0",
            outcome="improved",
            metrics={
                "accuracy": 0.75,
                "avg_response_length": 85,
                "grounding_score": 0.0,
                "latency_p95": 1250
            },
            failure_modes=[
                FailureMode(
                    id=str(uuid.uuid4()),
                    name="Hallucinated pricing",
                    description="Made up prices without access to real data",
                    severity="critical",
                    category="accuracy",
                    discovered_in_iteration=2,
                    resolution_status="fixed"
                )
            ],
            fixes_applied=[
                {"description": "Reduced max_tokens to 150", "iteration": 2}
            ]
        ))

    # V3: RAG-based, accurate
    if up_to_iteration >= 3:
        iterations.append(EvalIterationSummary(
            iteration=3,
            version_name="V3 RAG",
            prompt_version="v3.0",
            outcome="passed",
            metrics={
                "accuracy": 0.95,
                "avg_response_length": 82,
                "grounding_score": 0.92,
                "latency_p95": 1850
            },
            failure_modes=[],
            fixes_applied=[
                {"description": "Added ChromaDB RAG pipeline", "iteration": 3},
                {"description": "Added source citation requirement", "iteration": 3}
            ]
        ))

    return iterations


def create_sample_requirements() -> list:
    """Create sample requirement coverage"""
    return [
        RequirementCoverage(
            requirement_id="REQ-001",
            requirement_text="System must respond within 5 seconds (P95)",
            test_ids=["test_latency_p95", "test_performance_benchmark"],
            coverage_status="covered",
            verification_status="verified"
        ),
        RequirementCoverage(
            requirement_id="REQ-002",
            requirement_text="Responses must cite source documents",
            test_ids=["test_grounding_citations", "eval_v3_grounding"],
            coverage_status="covered",
            verification_status="verified"
        ),
        RequirementCoverage(
            requirement_id="REQ-003",
            requirement_text="No prompt injection vulnerabilities",
            test_ids=["test_prompt_injection", "test_security_validation"],
            coverage_status="covered",
            verification_status="verified"
        ),
        RequirementCoverage(
            requirement_id="REQ-004",
            requirement_text="Response length ~80 words (±25%)",
            test_ids=["eval_v1_length", "test_format_word_count"],
            coverage_status="covered",
            verification_status="verified"
        ),
        RequirementCoverage(
            requirement_id="REQ-005",
            requirement_text="Factual accuracy ≥85%",
            test_ids=["eval_v2_accuracy", "eval_v3_grounding"],
            coverage_status="covered",
            verification_status="verified"
        )
    ]


def seed_tsr_data():
    """Seed database with sample TSR data"""
    print("\n=== Seeding TSR Test Data ===")

    try:
        engine = create_engine(TSR_DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        repository = TSRRepository(session)
        evaluator = GoNoGoEvaluator()

        # Check if data already exists
        existing_count = repository.count()
        if existing_count > 0:
            print(f"⚠ Database already contains {existing_count} TSRs")
            print("  Skipping seeding (delete TSRs manually if you want to reseed)")
            return

        print("Creating sample TSRs for three iterations...")

        # Create TSRs for each iteration
        for iteration in range(1, 4):
            print(f"\nCreating TSR for V{iteration}...")

            tsr = TestSummaryReport(
                id=str(uuid.uuid4()),
                created_at=datetime.utcnow() - timedelta(days=10 - iteration * 3),
                triggered_by="seeding_script",
                environment="test",
                versions=create_sample_version_manifest(iteration),
                test_results=create_sample_test_results(iteration),
                eval_iterations=create_sample_eval_iterations(iteration),
                requirement_coverage=create_sample_requirements()
            )

            # Apply go/no-go decision
            evaluator.apply_decision(tsr)

            # Save to database
            repository.save(tsr)

            print(f"  ✓ Created TSR {tsr.id[:8]} with decision: {tsr.go_no_go_decision.value}")
            print(f"    Total tests: {tsr.get_total_tests()}, Passed: {tsr.get_total_passed()}")
            print(f"    Eval iterations: {len(tsr.eval_iterations)}")
            print(f"    Blocking issues: {len(tsr.blocking_issues)}")

        # Print summary
        total_tsrs = repository.count()
        go_count = repository.count(decision='go')
        no_go_count = repository.count(decision='no_go')

        print("\n" + "=" * 60)
        print(f"✓ Seeding complete!")
        print(f"  Total TSRs: {total_tsrs}")
        print(f"  GO decisions: {go_count}")
        print(f"  NO-GO decisions: {no_go_count}")
        print("=" * 60)

    except Exception as e:
        print(f"✗ Failed to seed test data: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    seed_tsr_data()
