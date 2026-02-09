"""Routes for the educational viewer"""

from flask import Blueprint, render_template, request, jsonify
import subprocess
from pathlib import Path

from .test_navigator import (
    get_tests_by_type,
    get_test_code,
    get_explanation,
    get_test_path,
    TEST_TYPES,
    get_ai_acceptance_tests,
)
from .trace_inspector import (
    get_traces_by_version,
    get_trace_detail,
    render_annotated_response,
)
from .iteration_timeline import get_iteration_summary, get_comparison_data
from .highlighting import syntax_highlight

viewer_bp = Blueprint("viewer", __name__)

# Legacy viewer routes removed - functionality integrated into narrative phases
# Helper functions are still used by narrative.py
