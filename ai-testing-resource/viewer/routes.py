"""Routes for the educational viewer"""

from flask import Blueprint, render_template, request, jsonify
import subprocess
from pathlib import Path

from .test_navigator import get_tests_by_type, get_test_code, get_explanation, get_test_path, TEST_TYPES, get_ai_acceptance_tests
from .trace_inspector import get_traces_by_version, get_trace_detail, render_annotated_response
from .iteration_timeline import get_iteration_summary, get_comparison_data
from .highlighting import syntax_highlight

viewer_bp = Blueprint('viewer', __name__)


@viewer_bp.route('/tests')
@viewer_bp.route('/tests/<test_type>')
def test_navigator(test_type='unit'):
    """Test Navigator page"""
    # Get AI acceptance tests for the sidebar
    ai_acceptance_tests = get_ai_acceptance_tests()

    # Handle ai_acceptance as a special test type
    if test_type == 'ai_acceptance':
        tests = ai_acceptance_tests
        explanation = get_explanation('ai_acceptance')
    else:
        tests = get_tests_by_type(test_type)
        explanation = get_explanation(test_type)

    # Get first test's code by default
    selected_test = request.args.get('test', tests[0]['id'] if tests else None)
    test_code = None
    test_filename = None
    app_code = None
    app_filename = None

    if selected_test:
        test_data = get_test_code(selected_test)
        test_code = syntax_highlight(test_data['code'])
        test_filename = test_data.get('filename', 'test.py')
        if test_data.get('related_app_code'):
            app_code = syntax_highlight(test_data['related_app_code'], muted=True)
            # Determine app filename from test name
            if 'sanitize' in selected_test or 'token' in selected_test or 'format' in selected_test:
                app_filename = 'app/utils.py'
            elif 'chroma' in selected_test or 'rag' in selected_test:
                app_filename = 'app/rag.py'
            else:
                app_filename = 'app/ai_service.py'

    return render_template('test_navigator.html',
                           active_nav='tests',
                           test_types=TEST_TYPES,
                           current_type=test_type,
                           tests=tests,
                           selected_test=selected_test,
                           test_code=test_code,
                           test_filename=test_filename,
                           app_code=app_code,
                           app_filename=app_filename,
                           explanation=explanation,
                           ai_acceptance_tests=ai_acceptance_tests)


@viewer_bp.route('/tests/run/<path:test_id>', methods=['POST'])
def run_test(test_id):
    """Run a single test and return result"""
    try:
        # Map test_id to file path
        test_path = get_test_path(test_id)

        if not test_path or not Path(test_path).exists():
            return jsonify({
                'status': 'fail',
                'output': f'Test file not found: {test_id}'
            })

        result = subprocess.run(
            ['pytest', test_path, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(Path(__file__).parent.parent)
        )

        return jsonify({
            'status': 'pass' if result.returncode == 0 else 'fail',
            'output': result.stdout + result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'fail',
            'output': 'Test timed out after 30 seconds'
        })
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'output': str(e)
        })


@viewer_bp.route('/traces')
@viewer_bp.route('/traces/<version>')
def trace_inspector(version='v1'):
    """Trace Inspector page"""
    traces = get_traces_by_version(version)

    selected_trace = request.args.get('trace', traces[0]['id'] if traces else None)
    trace_detail = None
    annotated_response = None

    if selected_trace:
        trace_detail = get_trace_detail(selected_trace)
        if trace_detail:
            annotated_response = render_annotated_response(
                trace_detail.get('response', ''),
                trace_detail.get('annotations', [])
            )

    return render_template('trace_inspector.html',
                           active_nav='traces',
                           current_version=version,
                           traces=traces,
                           selected_trace=selected_trace,
                           trace_detail=trace_detail,
                           annotated_response=annotated_response)


@viewer_bp.route('/timeline')
def iteration_timeline():
    """Iteration Timeline page"""
    summary = get_iteration_summary()
    comparison = get_comparison_data()

    return render_template('iteration_timeline.html',
                           active_nav='timeline',
                           summary=summary,
                           comparison=comparison)
