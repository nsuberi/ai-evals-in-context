"""Routes for the narrative educational journey

This module implements the linear narrative flow through Acme Widget Co's
journey from idea to production, with AI evals integrated alongside
traditional testing.
"""

from flask import Blueprint, render_template, request
from pathlib import Path
import markdown

from .test_navigator import get_tests_by_type, get_test_code, get_explanation, TEST_TYPES, get_ai_acceptance_tests
from .trace_inspector import get_traces_by_version, get_trace_detail, render_annotated_response
from .iteration_timeline import get_iteration_summary, get_comparison_data
from .highlighting import syntax_highlight

narrative_bp = Blueprint('narrative', __name__)

# Phase configuration for navigation and content
PHASES = {
    'landing': {
        'id': 'landing',
        'number': 0,
        'title': 'Welcome',
        'subtitle': "Follow Acme Widget Co's Journey",
        'short_title': 'Start',
        'url': '/',
        'next': 'problem',
        'prev': None,
    },
    'problem': {
        'id': 'problem',
        'number': 0,
        'title': 'The Problem',
        'subtitle': 'Understanding the Business Challenge',
        'short_title': 'Problem',
        'url': '/problem',
        'next': 'phase_1',
        'prev': 'landing',
    },
    'phase_1': {
        'id': 'phase_1',
        'number': 1,
        'title': 'Interview & Requirements',
        'subtitle': 'Understanding Stakeholder Needs',
        'short_title': 'Phase 1',
        'url': '/phase/1',
        'next': 'phase_2',
        'prev': 'problem',
    },
    'phase_2': {
        'id': 'phase_2',
        'number': 2,
        'title': 'Solution Design',
        'subtitle': 'Architecture & Testing Strategy',
        'short_title': 'Phase 2',
        'url': '/phase/2',
        'next': 'phase_3',
        'prev': 'phase_1',
    },
    'phase_3': {
        'id': 'phase_3',
        'number': 3,
        'title': 'Implementation',
        'subtitle': 'Building & Testing',
        'short_title': 'Phase 3',
        'url': '/phase/3',
        'next': 'phase_4',
        'prev': 'phase_2',
    },
    'phase_4': {
        'id': 'phase_4',
        'number': 4,
        'title': 'Pre-Production Evaluation',
        'subtitle': 'Iterating on AI Behavior',
        'short_title': 'Phase 4',
        'url': '/phase/4',
        'next': 'phase_5',
        'prev': 'phase_3',
    },
    'phase_5': {
        'id': 'phase_5',
        'number': 5,
        'title': 'Production Monitoring',
        'subtitle': 'Live Demo & Traces',
        'short_title': 'Phase 5',
        'url': '/phase/5',
        'next': 'governance',
        'prev': 'phase_4',
    },
    'governance': {
        'id': 'governance',
        'number': 6,
        'title': 'Governance',
        'subtitle': 'Compliance & Audit Trail',
        'short_title': 'Governance',
        'url': '/governance',
        'next': None,
        'prev': 'phase_5',
    },
}

# Ordered list of phases for navigation
PHASE_ORDER = ['landing', 'problem', 'phase_1', 'phase_2', 'phase_3', 'phase_4', 'phase_5', 'governance']


def load_narrative_content(filename):
    """Load and render markdown content from data/narrative/"""
    project_root = Path(__file__).parent.parent
    content_path = project_root / 'data' / 'narrative' / filename

    if content_path.exists():
        with open(content_path, 'r') as f:
            content = f.read()
        return markdown.markdown(content, extensions=['tables', 'fenced_code'])
    return None


def get_phase_context(phase_id):
    """Get navigation context for a phase"""
    phase = PHASES.get(phase_id)
    if not phase:
        return None

    prev_phase = PHASES.get(phase['prev']) if phase['prev'] else None
    next_phase = PHASES.get(phase['next']) if phase['next'] else None

    return {
        'phase': phase,
        'phases': PHASES,
        'phase_order': PHASE_ORDER,
        'prev_phase': prev_phase,
        'next_phase': next_phase,
        'active_nav': 'narrative',
    }


# ============================================
# Landing & Problem Routes
# ============================================

@narrative_bp.route('/')
def landing():
    """Landing page - introduces the 3-part cycle and 5 phases"""
    context = get_phase_context('landing')
    content = load_narrative_content('landing.md')
    return render_template('narrative/landing.html',
                           content=content,
                           **context)


@narrative_bp.route('/problem')
def problem():
    """Problem statement - Acme's business problem"""
    context = get_phase_context('problem')
    content = load_narrative_content('problem.md')
    return render_template('narrative/problem.html',
                           content=content,
                           **context)


# ============================================
# Phase Routes
# ============================================

@narrative_bp.route('/phase/1')
def phase_1():
    """Phase 1: Interview & Requirements"""
    context = get_phase_context('phase_1')

    # Load phase-specific content
    interview_content = load_narrative_content('phase1_interview.md')
    requirements_content = load_narrative_content('phase1_requirements.md')
    acceptance_content = load_narrative_content('phase1_acceptance.md')

    return render_template('narrative/phase1_interview.html',
                           interview_content=interview_content,
                           requirements_content=requirements_content,
                           acceptance_content=acceptance_content,
                           **context)


@narrative_bp.route('/phase/2')
def phase_2():
    """Phase 2: Solution Design"""
    context = get_phase_context('phase_2')

    # Load phase-specific content
    architecture_content = load_narrative_content('phase2_architecture.md')
    technology_content = load_narrative_content('phase2_technology.md')
    testing_content = load_narrative_content('phase2_testing.md')

    return render_template('narrative/phase2_design.html',
                           architecture_content=architecture_content,
                           technology_content=technology_content,
                           testing_content=testing_content,
                           **context)


@narrative_bp.route('/phase/3')
def phase_3():
    """Phase 3: Implementation - integrates Test Navigator"""
    context = get_phase_context('phase_3')
    intro_content = load_narrative_content('phase3_intro.md')

    # Get test navigator data (reuse existing functionality)
    test_type = request.args.get('test_type', 'unit')
    ai_acceptance_tests = get_ai_acceptance_tests()

    if test_type == 'ai_acceptance':
        tests = ai_acceptance_tests
        explanation = get_explanation('ai_acceptance')
    else:
        tests = get_tests_by_type(test_type)
        explanation = get_explanation(test_type)

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
            if 'sanitize' in selected_test or 'token' in selected_test or 'format' in selected_test:
                app_filename = 'app/utils.py'
            elif 'chroma' in selected_test or 'rag' in selected_test:
                app_filename = 'app/rag.py'
            else:
                app_filename = 'app/ai_service.py'

    return render_template('narrative/phase3_implementation.html',
                           intro_content=intro_content,
                           test_types=TEST_TYPES,
                           current_type=test_type,
                           tests=tests,
                           selected_test=selected_test,
                           test_code=test_code,
                           test_filename=test_filename,
                           app_code=app_code,
                           app_filename=app_filename,
                           explanation=explanation,
                           ai_acceptance_tests=ai_acceptance_tests,
                           **context)


@narrative_bp.route('/phase/4')
def phase_4():
    """Phase 4: Pre-Production Evaluation - integrates Trace Inspector + Timeline"""
    context = get_phase_context('phase_4')
    intro_content = load_narrative_content('phase4_intro.md')

    # Get trace inspector data
    version = request.args.get('version', 'v1')
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

    # Get timeline data
    summary = get_iteration_summary()
    comparison = get_comparison_data()

    return render_template('narrative/phase4_evaluation.html',
                           intro_content=intro_content,
                           current_version=version,
                           traces=traces,
                           selected_trace=selected_trace,
                           trace_detail=trace_detail,
                           annotated_response=annotated_response,
                           summary=summary,
                           comparison=comparison,
                           **context)


@narrative_bp.route('/phase/5')
def phase_5():
    """Phase 5: Production Monitoring - integrates Demo page"""
    context = get_phase_context('phase_5')
    intro_content = load_narrative_content('phase5_intro.md')

    # Default version for demo
    version = request.args.get('version', 'v3')

    return render_template('narrative/phase5_monitoring.html',
                           intro_content=intro_content,
                           selected_version=version,
                           **context)


@narrative_bp.route('/governance')
def governance():
    """Governance overview - cross-phase summary"""
    context = get_phase_context('governance')
    intro_content = load_narrative_content('governance_intro.md')

    return render_template('narrative/governance_overview.html',
                           intro_content=intro_content,
                           **context)
