#!/usr/bin/env python3
"""
CLI tool for generating Test Summary Reports from test results

Usage:
    python scripts/generate_tsr.py --results-dir results/ --codebase-sha abc123
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tsr.generator import TSRGenerator
from tsr.models import TestSummaryReport


def main():
    parser = argparse.ArgumentParser(
        description='Generate Test Summary Report from test results'
    )
    parser.add_argument(
        '--results-dir',
        required=True,
        help='Directory containing JUnit XML test results'
    )
    parser.add_argument(
        '--codebase-sha',
        required=True,
        help='Git SHA of the codebase being tested'
    )
    parser.add_argument(
        '--environment',
        default='test',
        choices=['test', 'staging', 'production'],
        help='Environment where tests were run (default: test)'
    )
    parser.add_argument(
        '--triggered-by',
        default='ci',
        help='Who/what triggered the test run (default: ci)'
    )
    parser.add_argument(
        '--output',
        default='tsr.json',
        help='Output file for TSR JSON (default: tsr.json)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )
    parser.add_argument(
        '--exit-on-no-go',
        action='store_true',
        help='Exit with code 1 if decision is NO-GO'
    )

    args = parser.parse_args()

    # Generate TSR
    print(f"Generating TSR from results in {args.results_dir}...")
    generator = TSRGenerator()

    try:
        tsr = generator.generate_from_junit_xml(
            results_dir=args.results_dir,
            codebase_sha=args.codebase_sha,
            environment=args.environment,
            triggered_by=args.triggered_by
        )

        # Write TSR to file
        tsr_dict = tsr.to_dict()
        indent = 2 if args.pretty else None

        with open(args.output, 'w') as f:
            json.dump(tsr_dict, f, indent=indent)

        print(f"✓ TSR generated successfully: {args.output}")
        print(f"  ID: {tsr.id}")
        print(f"  Decision: {tsr.go_no_go_decision.value.upper()}")
        print(f"  Reason: {tsr.decision_reason}")

        # Print summary
        print(f"\nTest Results:")
        for result in tsr.test_results:
            status = "✓" if result.failed == 0 else "✗"
            print(f"  {status} {result.test_type.value.upper()}: "
                  f"{result.passed}/{result.total} passed "
                  f"({result.pass_rate:.1%})")

        if tsr.blocking_issues:
            print(f"\nBlocking Issues ({len(tsr.blocking_issues)}):")
            for issue in tsr.blocking_issues:
                print(f"  ✗ {issue}")

        if tsr.warnings:
            print(f"\nWarnings ({len(tsr.warnings)}):")
            for warning in tsr.warnings:
                print(f"  ⚠ {warning}")

        # Exit with error code if NO-GO and flag is set
        if args.exit_on_no_go and tsr.go_no_go_decision.value == 'no_go':
            print("\n❌ Deployment blocked: NO-GO decision")
            sys.exit(1)

        print("\n✓ TSR generation complete")
        sys.exit(0)

    except Exception as e:
        print(f"✗ Error generating TSR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
