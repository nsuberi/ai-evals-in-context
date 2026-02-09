"""Routes for the narrative educational journey

This module implements the linear narrative flow through Acme Widget Co's
journey from idea to production, with AI evals integrated alongside
traditional testing.
"""

from flask import Blueprint, render_template, request, jsonify
from pathlib import Path
import markdown

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

# SDLC Role definitions (who creates / who validates)
SDLC_ROLES = {
    "DEV": {"name": "Developer", "color": "#3b82f6"},
    "TL": {"name": "Tech Lead", "color": "#8b5cf6"},
    "QA": {"name": "QA Engineer", "color": "#f59e0b"},
    "PO": {"name": "Product Owner", "color": "#10b981"},
    "SRE": {"name": "Site Reliability", "color": "#ef4444"},
    "GOV": {"name": "Governance / Risk", "color": "#6366f1"},
    "BIZ": {"name": "Business Stakeholder", "color": "#ec4899"},
}

# SDLC Test Types - adapted for PM/BA audience
SDLC_TESTS = [
    {
        "id": "unit",
        "name": "Unit Tests",
        "icon": "U",
        "color": "#3b82f6",
        "category": "traditional",
        "description": (
            "Unit tests verify that individual functions work correctly in isolation. "
            "Think of them as checking that each ingredient is fresh before cooking. "
            "They run in milliseconds and catch bugs immediately when code changes."
        ),
        "sdlc_role": (
            "Unit tests are the foundation of the testing pyramid. They give developers "
            "instant feedback during development and prevent regressions when code changes. "
            "A strong unit test suite means the team can move fast with confidence."
        ),
        "who_creates": ["DEV"],
        "who_validates": ["TL"],
        "ai_considerations": (
            "For AI features, unit tests verify the scaffolding: input sanitization, "
            "token counting, response formatting. They don't test AI behavior directly, "
            "but they ensure the plumbing works before you turn on the water."
        ),
        "audit_value": (
            "Unit test pass rates appear in TSR Section 2. A 100% pass rate signals "
            "that basic code quality is maintained across releases."
        ),
    },
    {
        "id": "integration",
        "name": "Integration Tests",
        "icon": "I",
        "color": "#8b5cf6",
        "category": "traditional",
        "description": (
            "Integration tests verify that components work together correctly. "
            "For an AI chatbot, this means testing that the retrieval pipeline connects "
            "to the vector database, fetches the right documents, and passes them to the LLM."
        ),
        "sdlc_role": (
            "Integration tests catch issues that unit tests miss\u2014problems that emerge "
            "when components interact. They're especially critical for AI systems where "
            "the pipeline has multiple stages (embed \u2192 retrieve \u2192 construct prompt \u2192 generate)."
        ),
        "who_creates": ["DEV", "TL"],
        "who_validates": ["QA", "TL"],
        "ai_considerations": (
            "RAG pipelines have many integration points: embedding models, vector stores, "
            "context window assembly, LLM APIs. Integration tests verify each handoff. "
            "When a retrieval model changes, these tests catch downstream impact."
        ),
        "audit_value": (
            "Integration test results in the TSR show that the system's components "
            "work together reliably. Governance reviewers look for coverage of "
            "critical data paths."
        ),
    },
    {
        "id": "e2e",
        "name": "End-to-End Tests",
        "icon": "E",
        "color": "#10b981",
        "category": "traditional",
        "description": (
            "End-to-end tests simulate a real user interacting with the full system. "
            "They verify the complete journey: user asks a question \u2192 system retrieves "
            "context \u2192 AI generates response \u2192 user sees answer with source citations."
        ),
        "sdlc_role": (
            "E2E tests are the closest thing to having a real user test your system. "
            "They catch problems that only appear when all layers work together, "
            "like a response that's technically correct but displayed incorrectly."
        ),
        "who_creates": ["QA", "DEV"],
        "who_validates": ["PO", "QA"],
        "ai_considerations": (
            "AI E2E tests must account for non-determinism. The same question might "
            "produce slightly different wording each time. Tests focus on structural "
            "properties (response contains source, stays under length limit) rather "
            "than exact text matches."
        ),
        "audit_value": (
            "E2E test results demonstrate that the system works from the user's "
            "perspective. Product owners can validate that the user experience "
            "matches requirements."
        ),
    },
    {
        "id": "performance",
        "name": "Performance Tests",
        "icon": "P",
        "color": "#f59e0b",
        "category": "traditional",
        "description": (
            "Performance tests measure response time, throughput, and resource usage "
            "under realistic load. For AI features, latency is critical\u2014users expect "
            "sub-5-second responses even when the system is busy."
        ),
        "sdlc_role": (
            "Performance tests prevent surprises in production. They establish baselines "
            "and catch regressions before deployment. A prompt change that increases "
            "token count can double latency\u2014performance tests catch this."
        ),
        "who_creates": ["DEV", "SRE"],
        "who_validates": ["SRE", "TL"],
        "ai_considerations": (
            "LLM inference latency is often the bottleneck. Performance tests should "
            "measure P50, P95, and P99 latencies separately for retrieval and generation "
            "steps. Monitor token usage to control cost per request."
        ),
        "audit_value": (
            "Performance benchmarks in the TSR show that the system meets SLAs. "
            "Governance teams use these to assess production readiness and "
            "capacity planning."
        ),
    },
    {
        "id": "acceptance",
        "name": "Acceptance Tests",
        "icon": "A",
        "color": "#ec4899",
        "category": "evolved",
        "description": (
            "Acceptance tests verify that the system meets the requirements agreed upon "
            "during discovery. They are the bridge between what stakeholders asked for "
            "and what was actually built. Business users own these criteria."
        ),
        "sdlc_role": (
            "Acceptance tests are the contract between builders and the business. "
            "They translate requirements like 'accurate pricing responses' into "
            "verifiable checks. When acceptance tests pass, the team has evidence "
            "that the feature is ready."
        ),
        "who_creates": ["PO", "QA"],
        "who_validates": ["BIZ", "GOV"],
        "ai_considerations": (
            "For AI features, acceptance criteria must account for probabilistic behavior. "
            "Instead of 'response equals X', criteria become 'response is accurate 95% "
            "of the time across N test cases'. This is where AI evals begin."
        ),
        "audit_value": (
            "Acceptance test results are the most important section of the TSR for "
            "governance reviewers. They directly map to business requirements and "
            "provide the evidence for go/no-go decisions."
        ),
    },
    {
        "id": "steel_thread",
        "name": "Steel Thread Tests",
        "icon": "S",
        "color": "#6366f1",
        "category": "evolved",
        "description": (
            "A steel thread test traces one complete path through the entire system, "
            "from user input to final output, verifying every integration point along "
            "the way. It's the thinnest possible end-to-end proof that the system works."
        ),
        "sdlc_role": (
            "Steel threads prove architectural viability early. Before building out "
            "all features, a steel thread confirms that the chosen architecture "
            "actually works. This reduces risk by validating assumptions."
        ),
        "who_creates": ["TL", "DEV"],
        "who_validates": ["TL", "SRE"],
        "ai_considerations": (
            "For RAG systems, the steel thread traces: user question \u2192 embedding \u2192 "
            "vector search \u2192 context assembly \u2192 prompt construction \u2192 LLM call \u2192 "
            "response formatting \u2192 source attribution. If any link breaks, "
            "the steel thread fails."
        ),
        "audit_value": (
            "Steel thread results in the TSR demonstrate that the full pipeline "
            "is operational. They're particularly valuable for initial deployments "
            "and major architecture changes."
        ),
    },
    {
        "id": "ai_acceptance",
        "name": "AI Acceptance Tests",
        "icon": "AI",
        "color": "#0f9b8e",
        "category": "new",
        "description": (
            "AI acceptance tests evaluate whether the AI's behavior meets business "
            "requirements. Unlike traditional tests with binary pass/fail, these assess "
            "qualities like accuracy, grounding, tone, and safety across many test cases."
        ),
        "sdlc_role": (
            "AI acceptance tests are the evolved form of acceptance testing for "
            "probabilistic systems. They run a suite of representative questions "
            "and measure aggregate pass rates against thresholds defined during discovery."
        ),
        "who_creates": ["DEV", "PO"],
        "who_validates": ["BIZ", "GOV"],
        "ai_considerations": (
            "These tests define 'what good looks like' for AI behavior. They evaluate "
            "grounding (does the response use the knowledge base?), accuracy (are facts "
            "correct?), format compliance (length, tone, structure), and safety (no "
            "harmful or off-topic content)."
        ),
        "audit_value": (
            "AI acceptance test results are the heart of the TSR for AI features. "
            "They provide quantified evidence that the AI meets the bar set by "
            "business stakeholders. Pass rates map directly to go/no-go criteria."
        ),
    },
    {
        "id": "evals",
        "name": "AI Evals",
        "icon": "EV",
        "color": "#0f9b8e",
        "category": "new",
        "description": (
            "AI evals are the systematic, ongoing evaluation of AI system behavior using "
            "trace data and human review. They go beyond automated tests to include "
            "qualitative assessment of response quality by domain experts."
        ),
        "sdlc_role": (
            "Evals provide the feedback loop that drives iteration. By reviewing actual "
            "traces and annotating failures, teams build a quantified picture of system "
            "quality that informs both improvement priorities and go/no-go decisions."
        ),
        "who_creates": ["PO", "DEV", "BIZ"],
        "who_validates": ["GOV", "BIZ"],
        "ai_considerations": (
            "Evals use qualitative coding methodology: each trace gets open codes "
            "(free-text observations) categorized into axial codes (standardized labels). "
            "This turns subjective quality assessment into countable evidence. "
            "Phase 4 demonstrates this methodology in action."
        ),
        "audit_value": (
            "Eval results populate TSR Section 3 (the 'money table'). Axial code "
            "counts across versions show improvement trends and remaining risks. "
            "Governance reviewers use these to assess whether the AI is production-ready."
        ),
    },
]

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
        "title": "Building and Testing with AI",
        "subtitle": "The SDLC Test Types That Senior Engineers Already Use",
        "short_title": "Build & Test",
        "url": "/phase/3",
        "next": "phase_4",
        "prev": "phase_2",
    },
    "phase_4": {
        "id": "phase_4",
        "number": 4,
        "title": "Iterate & Approve",
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
        "title": "TSR Evidence",
        "subtitle": "Compliance & Audit Trail",
        "short_title": "TSR Evidence",
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

# Narrative documents available for download
NARRATIVE_DOCUMENTS = [
    {
        "filename": "ai_evaluation_sdlc.pdf",
        "title": "AI Evaluation SDLC Overview",
        "description": "Complete guide to integrating AI evaluations into the software development lifecycle",
        "path": "/static/documents/ai_evaluation_sdlc.pdf",
    },
    {
        "filename": "sdlc_what_it_is.pdf",
        "title": "SDLC: What It Is and What It Isn't",
        "description": "Clarifying the purpose and misconceptions about the SDLC for AI systems",
        "path": "/static/documents/sdlc_what_it_is.pdf",
    },
    {
        "filename": "appendix_trace_capture.pdf",
        "title": "Appendix: Trace Capture Implementation",
        "description": "Technical appendix on implementing trace capture for AI system monitoring",
        "path": "/static/documents/appendix_trace_capture.pdf",
    },
    {
        "filename": "appendix_b_unified_monitoring.pdf",
        "title": "Appendix B: Unified Monitoring",
        "description": "Comprehensive monitoring strategy for AI applications in production",
        "path": "/static/documents/appendix_b_unified_monitoring.pdf",
    },
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
    return render_template(
        "narrative/landing.html",
        content=content,
        documents=NARRATIVE_DOCUMENTS,
        **context,
    )


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
    """Phase 3: Build & Test - SDLC test types as a common language"""
    context = get_phase_context("phase_3")
    intro_content = load_narrative_content("phase3_intro.md")

    return render_template(
        "narrative/phase3_implementation.html",
        intro_content=intro_content,
        sdlc_tests=SDLC_TESTS,
        sdlc_roles=SDLC_ROLES,
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
