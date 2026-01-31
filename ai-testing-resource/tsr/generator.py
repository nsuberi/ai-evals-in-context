"""TSR generation from test results"""

import xml.etree.ElementTree as ET
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from .models import (
    TestSummaryReport, VersionManifest, TestTypeResult,
    EvalIterationSummary, RequirementCoverage, TestType, FailureMode
)
from .rules import GoNoGoEvaluator


class TSRGenerator:
    """Generates Test Summary Reports from test results"""

    def __init__(self):
        self.evaluator = GoNoGoEvaluator()

    def generate_from_junit_xml(
        self,
        results_dir: str,
        codebase_sha: str,
        environment: str = "test",
        triggered_by: str = "ci"
    ) -> TestSummaryReport:
        """Generate TSR from JUnit XML test results

        Args:
            results_dir: Directory containing JUnit XML files
            codebase_sha: Git SHA of the codebase
            environment: Test environment (test, staging, production)
            triggered_by: Who/what triggered the test run

        Returns:
            TestSummaryReport
        """
        tsr = TestSummaryReport(
            created_at=datetime.utcnow(),
            triggered_by=triggered_by,
            environment=environment
        )

        # Collect version information
        tsr.versions = self._collect_version_manifest(codebase_sha)

        # Parse test results from XML files
        results_path = Path(results_dir)
        for xml_file in results_path.glob('*.xml'):
            test_type = self._infer_test_type(xml_file.name)
            result = self._parse_junit_xml(xml_file, test_type)
            if result:
                tsr.test_results.append(result)

        # Look for eval results JSON file
        eval_file = results_path / 'eval_results.json'
        if eval_file.exists():
            tsr.eval_iterations = self._parse_eval_results(eval_file)

        # Look for requirement coverage JSON file
        coverage_file = results_path / 'requirement_coverage.json'
        if coverage_file.exists():
            tsr.requirement_coverage = self._parse_requirement_coverage(coverage_file)

        # Apply go/no-go evaluation
        self.evaluator.apply_decision(tsr)

        return tsr

    def _collect_version_manifest(self, codebase_sha: str) -> VersionManifest:
        """Collect version information from git

        Args:
            codebase_sha: Git SHA of the codebase

        Returns:
            VersionManifest
        """
        try:
            # Get current branch
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                text=True
            ).strip()

            # Get repo URL
            repo = subprocess.check_output(
                ['git', 'config', '--get', 'remote.origin.url'],
                text=True
            ).strip()

            # For simplicity, use codebase SHA for tests and prompts
            # In production, these would point to separate repos
            testbase_sha = codebase_sha
            prompts_sha = codebase_sha

            return VersionManifest(
                codebase_sha=codebase_sha,
                codebase_branch=branch,
                codebase_repo=repo,
                testbase_sha=testbase_sha,
                prompts_sha=prompts_sha,
                prompts_version=None
            )
        except subprocess.CalledProcessError:
            # Fallback if git commands fail
            return VersionManifest(
                codebase_sha=codebase_sha,
                codebase_branch='unknown',
                codebase_repo='unknown',
                testbase_sha=codebase_sha,
                prompts_sha=codebase_sha
            )

    def _infer_test_type(self, filename: str) -> TestType:
        """Infer test type from filename

        Args:
            filename: XML filename

        Returns:
            TestType
        """
        filename_lower = filename.lower()
        if 'unit' in filename_lower:
            return TestType.UNIT
        elif 'integration' in filename_lower:
            return TestType.INTEGRATION
        elif 'e2e' in filename_lower or 'end' in filename_lower:
            return TestType.E2E
        elif 'acceptance' in filename_lower:
            return TestType.ACCEPTANCE
        elif 'eval' in filename_lower:
            return TestType.EVALS
        elif 'security' in filename_lower:
            return TestType.SECURITY
        elif 'performance' in filename_lower or 'perf' in filename_lower:
            return TestType.PERFORMANCE
        else:
            return TestType.UNIT  # Default

    def _parse_junit_xml(self, xml_file: Path, test_type: TestType) -> Optional[TestTypeResult]:
        """Parse JUnit XML file

        Args:
            xml_file: Path to JUnit XML file
            test_type: Type of test

        Returns:
            TestTypeResult or None if parsing fails
        """
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # JUnit XML can have either <testsuite> or <testsuites> as root
            if root.tag == 'testsuites':
                suites = root.findall('testsuite')
            else:
                suites = [root]

            total = 0
            passed = 0
            failed = 0
            skipped = 0
            duration_ms = 0
            failure_details = []

            for suite in suites:
                total += int(suite.get('tests', 0))
                failed += int(suite.get('failures', 0))
                failed += int(suite.get('errors', 0))
                skipped += int(suite.get('skipped', 0))

                # Duration is usually in seconds in JUnit XML
                time_str = suite.get('time', '0')
                duration_ms += int(float(time_str) * 1000)

                # Collect failure details
                for testcase in suite.findall('testcase'):
                    failure = testcase.find('failure')
                    error = testcase.find('error')

                    if failure is not None or error is not None:
                        elem = failure if failure is not None else error
                        failure_details.append({
                            'test_name': testcase.get('name'),
                            'class_name': testcase.get('classname'),
                            'message': elem.get('message', ''),
                            'type': elem.get('type', ''),
                            'details': elem.text or ''
                        })

            passed = total - failed - skipped

            return TestTypeResult(
                test_type=test_type,
                total=total,
                passed=passed,
                failed=failed,
                skipped=skipped,
                duration_ms=duration_ms,
                failure_details=failure_details
            )

        except Exception as e:
            print(f"Error parsing {xml_file}: {e}")
            return None

    def _parse_eval_results(self, json_file: Path) -> List[EvalIterationSummary]:
        """Parse eval results from JSON file

        Expected format:
        {
            "iterations": [
                {
                    "iteration": 1,
                    "version_name": "V1 Verbose",
                    "prompt_version": "v1.0",
                    "outcome": "failed",
                    "metrics": {"accuracy": 0.65, ...},
                    "failure_modes": [...],
                    "fixes_applied": [...]
                }
            ]
        }

        Args:
            json_file: Path to eval results JSON

        Returns:
            List of EvalIterationSummary
        """
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            iterations = []
            for item in data.get('iterations', []):
                failure_modes = [
                    FailureMode.from_dict(fm) for fm in item.get('failure_modes', [])
                ]

                iterations.append(EvalIterationSummary(
                    iteration=item['iteration'],
                    version_name=item['version_name'],
                    prompt_version=item['prompt_version'],
                    outcome=item['outcome'],
                    metrics=item['metrics'],
                    failure_modes=failure_modes,
                    fixes_applied=item.get('fixes_applied', [])
                ))

            return iterations

        except Exception as e:
            print(f"Error parsing eval results: {e}")
            return []

    def _parse_requirement_coverage(self, json_file: Path) -> List[RequirementCoverage]:
        """Parse requirement coverage from JSON file

        Expected format:
        {
            "requirements": [
                {
                    "requirement_id": "REQ-001",
                    "requirement_text": "System must...",
                    "test_ids": ["test_unit_001", ...],
                    "coverage_status": "covered",
                    "verification_status": "verified"
                }
            ]
        }

        Args:
            json_file: Path to requirement coverage JSON

        Returns:
            List of RequirementCoverage
        """
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            coverage = []
            for item in data.get('requirements', []):
                coverage.append(RequirementCoverage(
                    requirement_id=item['requirement_id'],
                    requirement_text=item['requirement_text'],
                    test_ids=item['test_ids'],
                    coverage_status=item['coverage_status'],
                    verification_status=item['verification_status']
                ))

            return coverage

        except Exception as e:
            print(f"Error parsing requirement coverage: {e}")
            return []
