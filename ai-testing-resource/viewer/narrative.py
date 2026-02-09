"""Routes for the narrative educational journey

This module implements the linear narrative flow through Acme Widget Co's
journey from idea to production, with AI evals integrated alongside
traditional testing.
"""

from flask import Blueprint, render_template, request, jsonify
from pathlib import Path
import markdown

from .test_navigator import get_explanation, TEST_TYPES
from .trace_inspector import (
    get_traces_by_version,
    get_trace_detail,
    render_annotated_response,
    AXIAL_CODES,
    get_annotation_summary,
)
from .iteration_timeline import (
    get_iteration_summary,
    get_comparison_data,
    get_failure_modes,
    get_architecture_context,
)

narrative_bp = Blueprint("narrative", __name__)

# Phase configuration for navigation and content
PHASES = {
    "landing": {
        "id": "landing",
        "number": 0,
        "title": "AI in Production",
        "subtitle": "A Governance-First Approach",
        "short_title": "Start",
        "url": "/",
        "next": "problem",
        "prev": None,
    },
    "problem": {
        "id": "problem",
        "number": 0,
        "title": "The Problem",
        "subtitle": "Understanding the Business Challenge",
        "short_title": "Problem",
        "url": "/problem",
        "next": "phase_1",
        "prev": "landing",
    },
    "phase_1": {
        "id": "phase_1",
        "number": 1,
        "title": "Interviewing to Discover Requirements",
        "subtitle": "Understanding Stakeholder Needs Through Discovery",
        "short_title": "Discovery",
        "url": "/phase/1",
        "next": "phase_2",
        "prev": "problem",
    },
    "phase_2": {
        "id": "phase_2",
        "number": 2,
        "title": "Planning a Solution Design",
        "subtitle": "Architecture, Technology & Testing Strategy",
        "short_title": "Design",
        "url": "/phase/2",
        "next": "phase_3",
        "prev": "phase_1",
    },
    "phase_3": {
        "id": "phase_3",
        "number": 3,
        "title": "Building with AI",
        "subtitle": "Test Types as the Path to Quality",
        "short_title": "Build",
        "url": "/phase/3",
        "next": "phase_4",
        "prev": "phase_2",
    },
    "phase_4": {
        "id": "phase_4",
        "number": 4,
        "title": "Building AI Features",
        "subtitle": "Iterating Through Failure Modes",
        "short_title": "Iterate & Approve",
        "url": "/phase/4",
        "next": "phase_5",
        "prev": "phase_3",
    },
    "phase_5": {
        "id": "phase_5",
        "number": 5,
        "title": "Continuous Monitoring",
        "subtitle": "Production Feedback & Observation",
        "short_title": "Deploy & Monitor",
        "url": "/phase/5",
        "next": "governance",
        "prev": "phase_4",
    },
    "governance": {
        "id": "governance",
        "number": 6,
        "title": "Governance",
        "subtitle": "Compliance & Audit Trail",
        "short_title": "Governance",
        "url": "/governance",
        "next": None,
        "prev": "phase_5",
    },
}

# Ordered list of phases for navigation
PHASE_ORDER = [
    "landing",
    "problem",
    "phase_1",
    "phase_2",
    "phase_3",
    "phase_4",
    "phase_5",
    "governance",
]


def load_narrative_content(filename):
    """Load and render markdown content from data/narrative/"""
    project_root = Path(__file__).parent.parent
    content_path = project_root / "data" / "narrative" / filename

    if content_path.exists():
        with open(content_path, "r") as f:
            content = f.read()
        return markdown.markdown(content, extensions=["tables", "fenced_code"])
    return None


def get_phase_context(phase_id):
    """Get navigation context for a phase"""
    phase = PHASES.get(phase_id)
    if not phase:
        return None

    prev_phase = PHASES.get(phase["prev"]) if phase["prev"] else None
    next_phase = PHASES.get(phase["next"]) if phase["next"] else None

    return {
        "phase": phase,
        "phases": PHASES,
        "phase_order": PHASE_ORDER,
        "prev_phase": prev_phase,
        "next_phase": next_phase,
        "active_nav": "narrative",
    }


# ============================================
# Landing & Problem Routes
# ============================================


@narrative_bp.route("/")
def landing():
    """Landing page - introduces the 3-part cycle and 5 phases"""
    context = get_phase_context("landing")
    content = load_narrative_content("landing.md")
    return render_template("narrative/landing.html", content=content, **context)


@narrative_bp.route("/problem")
def problem():
    """Problem statement - Acme's business problem"""
    context = get_phase_context("problem")
    content = load_narrative_content("problem.md")
    return render_template("narrative/problem.html", content=content, **context)


# ============================================
# Phase Routes
# ============================================


@narrative_bp.route("/phase/1")
def phase_1():
    """Phase 1: Interview & Requirements"""
    context = get_phase_context("phase_1")

    # Load phase-specific content
    interview_content = load_narrative_content("phase1_interview.md")
    requirements_content = load_narrative_content("phase1_requirements.md")
    acceptance_content = load_narrative_content("phase1_acceptance.md")

    return render_template(
        "narrative/phase1_interview.html",
        interview_content=interview_content,
        requirements_content=requirements_content,
        acceptance_content=acceptance_content,
        **context,
    )


@narrative_bp.route("/phase/2")
def phase_2():
    """Phase 2: Solution Design"""
    context = get_phase_context("phase_2")

    # Load phase-specific content
    architecture_content = load_narrative_content("phase2_architecture.md")
    technology_content = load_narrative_content("phase2_technology.md")
    testing_content = load_narrative_content("phase2_testing.md")

    return render_template(
        "narrative/phase2_design.html",
        architecture_content=architecture_content,
        technology_content=technology_content,
        testing_content=testing_content,
        **context,
    )


@narrative_bp.route("/phase/3")
def phase_3():
    """Phase 3: Building with AI - test types as a common language"""
    context = get_phase_context("phase_3")
    intro_content = load_narrative_content("phase3_intro.md")

    # Load explanations for ALL test types (for card grid display)
    all_type_explanations = {}
    for t in TEST_TYPES:
        all_type_explanations[t["id"]] = get_explanation(t["id"])
    all_type_explanations["ai_acceptance"] = get_explanation("ai_acceptance")

    # Business-facing test types get a special badge
    business_facing_types = {"acceptance", "ai_acceptance", "evals"}

    return render_template(
        "narrative/phase3_implementation.html",
        intro_content=intro_content,
        test_types=TEST_TYPES,
        all_type_explanations=all_type_explanations,
        business_facing_types=business_facing_types,
        **context,
    )


@narrative_bp.route("/phase/4")
def phase_4():
    """Phase 4: Building AI Features - integrates Trace Inspector + Timeline"""
    context = get_phase_context("phase_4")
    intro_content = load_narrative_content("phase4_intro.md")

    # Get trace inspector data
    version = request.args.get("version", "v1")
    traces = get_traces_by_version(version)

    selected_trace = request.args.get("trace", traces[0]["id"] if traces else None)
    trace_detail = None
    annotated_response = None

    if selected_trace:
        trace_detail = get_trace_detail(selected_trace)
        if trace_detail:
            annotated_response = render_annotated_response(
                trace_detail.get("response", ""), trace_detail.get("annotations", [])
            )

    # Get timeline data
    summary = get_iteration_summary()
    comparison = get_comparison_data()

    # Get failure modes and architecture context for current version
    failure_modes = get_failure_modes(version)
    arch_context = get_architecture_context(version)

    # Annotation methodology data
    axial_codes = AXIAL_CODES
    annotation_summary = get_annotation_summary()

    return render_template(
        "narrative/phase4_evaluation.html",
        intro_content=intro_content,
        current_version=version,
        traces=traces,
        selected_trace=selected_trace,
        trace_detail=trace_detail,
        annotated_response=annotated_response,
        summary=summary,
        comparison=comparison,
        failure_modes=failure_modes,
        arch_context=arch_context,
        axial_codes=axial_codes,
        annotation_summary=annotation_summary,
        **context,
    )


@narrative_bp.route("/api/phase4/trace/<version>/<trace_id>")
def api_get_trace(version: str, trace_id: str):
    """API endpoint for AJAX trace fetching (no page reload)."""
    trace_detail = get_trace_detail(trace_id)
    if not trace_detail:
        return jsonify({"error": "Trace not found"}), 404

    # Render annotated response server-side
    annotated_response = render_annotated_response(
        trace_detail.get("response", ""), trace_detail.get("annotations", [])
    )

    return jsonify(
        {
            "trace_id": trace_id,
            "version": version,
            "trace_detail": trace_detail,
            "annotated_response": annotated_response,
            "has_spans": "spans" in trace_detail
            and len(trace_detail.get("spans", [])) > 0,
        }
    )


@narrative_bp.route("/api/phase4/version/<version>")
def api_get_version(version: str):
    """API endpoint for AJAX version switching (no page reload)."""
    if version not in ("v1", "v2", "v3"):
        return jsonify({"error": "Invalid version"}), 400

    traces = get_traces_by_version(version)
    selected_trace_id = traces[0]["id"] if traces else None

    trace_detail = None
    annotated_response = None
    has_spans = False
    if selected_trace_id:
        trace_detail = get_trace_detail(selected_trace_id)
        if trace_detail:
            annotated_response = render_annotated_response(
                trace_detail.get("response", ""),
                trace_detail.get("annotations", []),
            )
            has_spans = (
                "spans" in trace_detail and len(trace_detail.get("spans", [])) > 0
            )

    failure_modes = get_failure_modes(version)
    arch_context = get_architecture_context(version)

    return jsonify(
        {
            "version": version,
            "traces": traces,
            "selected_trace_id": selected_trace_id,
            "trace_detail": trace_detail,
            "annotated_response": annotated_response,
            "has_spans": has_spans,
            "failure_modes": failure_modes,
            "arch_context": arch_context,
            "annotation_summary": get_annotation_summary(),
            "axial_codes": AXIAL_CODES,
        }
    )


@narrative_bp.route("/api/phase4/axial-codes")
def api_axial_codes():
    """API endpoint returning axial code definitions and per-version summary."""
    return jsonify(
        {
            "axial_codes": AXIAL_CODES,
            "summary": get_annotation_summary(),
        }
    )


@narrative_bp.route("/phase/5")
def phase_5():
    """Phase 5: Production Monitoring - integrates Demo page"""
    context = get_phase_context("phase_5")
    intro_content = load_narrative_content("phase5_intro.md")

    # Default version for demo
    version = request.args.get("version", "v3")

    return render_template(
        "narrative/phase5_monitoring.html",
        intro_content=intro_content,
        selected_version=version,
        **context,
    )


@narrative_bp.route("/governance")
def governance():
    """Governance overview - inline TSR cards from database"""
    context = get_phase_context("governance")
    intro_content = load_narrative_content("governance_intro.md")

    # Get TSR data from repository
    from .governance import _repository

    tsrs = []
    stats = None
    if _repository:
        tsrs = _repository.query(limit=10)
        total = _repository.count()
        go = _repository.count(decision="go")
        no_go = _repository.count(decision="no_go")
        stats = {
            "total": total,
            "go": go,
            "no_go": no_go,
            "go_rate": go / total if total > 0 else 0,
        }

    return render_template(
        "narrative/governance_overview.html",
        intro_content=intro_content,
        tsrs=tsrs,
        stats=stats,
        **context,
    )
