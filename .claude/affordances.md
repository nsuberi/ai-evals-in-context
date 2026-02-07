# Project Affordances Reference

> Living bill of materials for the AI Testing Resource project.
> Last updated: 2026-02-07

## Places

| Place | Status | Route | Template | Description |
|-------|--------|-------|----------|-------------|
| Landing | existing | `/` | `narrative/landing.html` | Governance-first intro with rainbow arc, 5-phase overview |
| Problem | existing | `/problem` | `narrative/problem.html` | Acme Widget Co business challenge |
| Phase 1: Discovery | existing | `/phase/1` | `narrative/phase1_interview.html` | Stakeholder interviews, requirements, acceptance criteria |
| Phase 2: Design | existing | `/phase/2` | `narrative/phase2_design.html` | Architecture, technology, testing strategy |
| Phase 3: Build | existing | `/phase/3` | `narrative/phase3_implementation.html` | Test type card grid, code canvas, test navigator |
| Phase 4: Iterate | existing | `/phase/4` | `narrative/phase4_evaluation.html` | Trace inspector, timeline, failure modes, architecture context |
| Phase 5: Monitor | existing | `/phase/5` | `narrative/phase5_monitoring.html` | Production demo, feedback loop to Phase 1 |
| Governance | existing | `/governance` | `narrative/governance_overview.html` | Cross-phase compliance and audit trail |
| Ask (Demo) | existing | `/ask` | `ask.html` | Live support bot demo with version selector |
| Test Navigator | existing | `/viewer/tests` | `test_navigator.html` | Browse/run tests by type with code viewer |
| Trace Inspector | existing | `/viewer/traces` | `trace_inspector.html` | View AI interaction traces with annotations |
| Iteration Timeline | existing | `/viewer/timeline` | `iteration_timeline.html` | Compare versions side-by-side |
| Governance Dashboard | existing | `/governance/dashboard` | `governance/dashboard.html` | TSR list with filtering and stats |
| TSR Detail | existing | `/governance/tsr/<id>` | `governance/tsr_detail.html` | Single TSR detailed view with approval |
| TSR Compare | existing | `/governance/compare` | `governance/comparison.html` | Side-by-side TSR comparison |
| Health Check | existing | `/health` | (JSON) | Service health endpoint |

## UI Affordances

| ID | Affordance | Place(s) | Description |
|----|-----------|----------|-------------|
| U1 | Phase navigation | All narrative pages | Horizontal nav rendering from `PHASES` dict via `phase_nav.html` component |
| U2 | Rainbow arc | Landing | SVG arc visualization of 5 phases |
| U3 | Test type card grid | Phase 3 | Cards for each test type with explanations |
| U4 | Code canvas | Phase 3, Test Navigator | Syntax-highlighted code display with filename tab, line numbers, run button |
| U5 | Collapsible section | Phase 3, others | Expandable content sections |
| U6 | Trace sidebar | Phase 4, Trace Inspector | List of traces for selected version, clickable to load detail |
| U7 | Annotation markers | Phase 4, Trace Inspector | Inline `<sup>` markers on annotated response text with severity coloring |
| U8 | Version selector tabs | Phase 4, Ask | `v1`/`v2`/`v3` tabs to switch prompt versions |
| U9 | Failure modes panel | Phase 4 | Displays failure modes for selected version |
| U10 | Architecture context panel | Phase 4 | Shows prompt strategy, architecture, limitations per version |
| U11 | Comparison metrics table | Phase 4, Iteration Timeline | Side-by-side version comparison |
| U12 | Question input form | Ask | Text input + version selector + submit for live demo |
| U13 | Response display | Ask | Rendered AI response with sources and metadata |
| U14 | Test runner button | Test Navigator, Phase 3 | POST to `/viewer/tests/run/<id>` and display pass/fail |
| U15 | TSR filter controls | Governance Dashboard | Environment and decision dropdowns |
| U16 | TSR approval form | TSR Detail | Approver name input + approve button |
| U17 | TSR comparison selector | Governance Dashboard | Checkbox selection for side-by-side compare |
| U18 | Artifact card | Various | Reusable card component for displaying artifacts |
| U19 | Narrative content sections | All phases | Markdown-rendered content blocks loaded from `data/narrative/` |
| U20 | Prev/Next navigation | All narrative pages | Phase-to-phase navigation links |

## Code Affordances

| ID | Affordance | Module | Description |
|----|-----------|--------|-------------|
| N1 | `create_app()` | `app/__init__.py` | Flask app factory: configures loaders, registers 5 blueprints, sets up DB session |
| N2 | `combine_prefix()` | `app/__init__.py` | Combines APPLICATION_ROOT with blueprint prefix for proxy routing |
| N3 | `setup_database_session()` | `app/__init__.py` | `before_request`/`teardown_appcontext` hooks for SQLAlchemy session lifecycle |
| N4 | `ask()` | `app/ai_service.py` | Main entry point routing to `ask_v1`/`ask_v2`/`ask_v3` by version string |
| N5 | `ask_v1()` | `app/ai_service.py` | Verbose 300-word prompt, direct Claude API call, no RAG |
| N6 | `ask_v2()` | `app/ai_service.py` | Concise 80-word prompt, no RAG, hallucinates facts |
| N7 | `ask_v3()` | `app/ai_service.py` | RAG pipeline: ChromaDB retrieval + context injection + Claude API |
| N8 | `get_client()` | `app/ai_service.py` | Lazy Anthropic client initialization from env key |
| N9 | `get_relevant_docs()` | `app/rag.py` | ChromaDB similarity search returning top-N documents |
| N10 | `initialize_knowledge_base()` | `app/rag.py` | Loads markdown files from `data/knowledge_base/` into ChromaDB |
| N11 | `get_collection()` | `app/rag.py` | Lazy ChromaDB collection initialization with sentence-transformer embeddings |
| N12 | `sanitize_input()` | `app/utils.py` | Strips HTML, null bytes, limits length, normalizes whitespace |
| N13 | `format_response()` | `app/utils.py` | Structures AI output into `{text, sources, metadata, trace}` dict |
| N14 | `count_tokens()` | `app/utils.py` | Token counting via tiktoken |
| N15 | `convert_markdown_to_html()` | `app/utils.py` | Markdown-to-HTML with fenced_code, tables, nl2br extensions |
| N16 | `PHASES` dict | `viewer/narrative.py` | Phase configuration: id, number, title, subtitle, short_title, url, prev/next |
| N17 | `PHASE_ORDER` list | `viewer/narrative.py` | Ordered phase IDs for navigation rendering |
| N18 | `load_narrative_content()` | `viewer/narrative.py` | Loads and renders markdown from `data/narrative/` with tables + fenced_code |
| N19 | `get_phase_context()` | `viewer/narrative.py` | Builds nav context: current phase, prev/next, all phases |
| N20 | `get_tests_by_type()` | `viewer/test_navigator.py` | Scans `tests/<type>/` directory for test files |
| N21 | `get_test_code()` | `viewer/test_navigator.py` | Reads test file + finds related app code via `find_related_app_code()` |
| N22 | `get_explanation()` | `viewer/test_navigator.py` | Loads markdown explanation from `data/explanations/<type>.md` |
| N23 | `TEST_TYPES` list | `viewer/test_navigator.py` | 8 test types: unit, integration, e2e, acceptance, evals, security, performance, steelthread |
| N24 | `get_ai_acceptance_tests()` | `viewer/test_navigator.py` | Scans `tests/ai_acceptance/` for AI-specific acceptance tests |
| N25 | `get_traces_by_version()` | `viewer/trace_inspector.py` | Loads trace list from `data/traces/<version>_traces.json` |
| N26 | `get_trace_detail()` | `viewer/trace_inspector.py` | Finds specific trace by ID across all version files |
| N27 | `render_annotated_response()` | `viewer/trace_inspector.py` | Inserts `<span class="ann">` markers into response text at annotation positions |
| N28 | `get_trace_summary()` | `viewer/trace_inspector.py` | Aggregate stats: count, avg latency/tokens, error/warning/success counts |
| N29 | `VERSIONS` list | `viewer/iteration_timeline.py` | Version metadata: id, name, subtitle, color, problem, fix, prompt_change |
| N30 | `FAILURE_MODES` dict | `viewer/iteration_timeline.py` | Per-version failure modes with severity, description, resolution |
| N31 | `ARCHITECTURE_CONTEXT` dict | `viewer/iteration_timeline.py` | Per-version prompt strategy, architecture, limitations |
| N32 | `get_iteration_summary()` | `viewer/iteration_timeline.py` | Combines `VERSIONS` with trace summary stats |
| N33 | `get_comparison_data()` | `viewer/iteration_timeline.py` | Comparison metrics + key lessons for timeline view |
| N34 | `syntax_highlight()` | `viewer/highlighting.py` | Pygments-based syntax highlighting, supports muted mode |
| N35 | `ANNOTATION_TYPES` dict | `viewer/annotations.py` | 6 annotation types with default severity |
| N36 | `annotate_*` functions | `viewer/annotations.py` | Length, hallucination, missing source, correct retrieval, accurate answer checkers |
| N37 | `TSRRepository` class | `tsr/repository.py` | CRUD operations: save, get_by_id, get_latest, query, count, delete |
| N38 | `GoNoGoEvaluator` class | `tsr/rules.py` | Rules engine: evaluates TSR against blocking/warning conditions |
| N39 | `TestSummaryReport` model | `tsr/models.py` | Dataclass with version manifest, test results, eval iterations, coverage |
| N40 | `GoNoGoDecision` enum | `tsr/models.py` | GO, NO_GO, PENDING_REVIEW deployment decisions |
| N41 | `TSRModel` + related | `tsr/database.py` | SQLAlchemy ORM models: TSR, TestResult, EvalIteration, RequirementCoverage |
| N42 | `create_tables()` | `tsr/database.py` | SQLAlchemy `Base.metadata.create_all()` for schema creation |
| N43 | `init_tsr_api()` | `tsr/api.py` | Sets global `_repository` for TSR API blueprint routes |
| N44 | `init_governance()` | `viewer/governance.py` | Sets global `_repository` for governance blueprint routes |
| N45 | `tsr_api` blueprint | `tsr/api.py` | REST API: POST create, GET by id/latest/query/stats, POST approve, DELETE |
| N46 | `governance` blueprint | `viewer/governance.py` | Dashboard, TSR detail, approval, comparison views |
| N47 | `narrative_bp` blueprint | `viewer/narrative.py` | All narrative phase routes (landing through governance) |
| N48 | `app_bp` blueprint | `app/routes.py` | `/ask` route (GET form + POST question handler) |
| N49 | `viewer_bp` blueprint | `viewer/routes.py` | `/viewer/tests`, `/viewer/traces`, `/viewer/timeline` routes |
| N50 | `ask_route()` | `app/routes.py` | Handles GET (render form) and POST (sanitize + call `ask()` + return JSON) |
| N51 | `run_test()` | `viewer/routes.py` | POST endpoint: runs pytest subprocess on a specific test file |
| N52 | `get_database_url()` | `config.py` | Resolves DB URL from env vars with SQLite fallback |
| N53 | `Question`/`Response`/`KnowledgeDoc` | `app/models.py` | Domain dataclasses for the support bot |
| N54 | `LineSelection` dataclass | `viewer/code_selection.py` | Represents selected lines; URL param serialization |
| N55 | `get_line_content()` | `viewer/code_selection.py` | Extracts specific lines from a file |
| N56 | `add_line_numbers()` | `viewer/code_selection.py` | Adds line number gutter HTML to code |
| N57 | `TSRGenerator` class | `tsr/generator.py` | Generates TSRs from JUnit XML + eval JSON + git info |

## Data Affordances

| ID | Affordance | Path | Description |
|----|-----------|------|-------------|
| D1 | Knowledge base: return_policy | `data/knowledge_base/return_policy.md` | Acme return/refund policies |
| D2 | Knowledge base: pricing_tiers | `data/knowledge_base/pricing_tiers.md` | Product pricing information |
| D3 | Knowledge base: product_specs | `data/knowledge_base/product_specs.md` | Product specifications |
| D4 | Knowledge base: shipping_info | `data/knowledge_base/shipping_info.md` | Shipping options and policies |
| D5 | V1 traces | `data/traces/v1_traces.json` | 20 verbose response traces with annotations |
| D6 | V2 traces | `data/traces/v2_traces.json` | 20 hallucinating response traces with annotations |
| D7 | V3 traces | `data/traces/v3_traces.json` | 20 RAG-grounded response traces with annotations |
| D8 | Narrative: landing | `data/narrative/landing.md` | Landing page markdown content |
| D9 | Narrative: problem | `data/narrative/problem.md` | Problem statement content |
| D10 | Narrative: phase1_interview | `data/narrative/phase1_interview.md` | Phase 1 interview content |
| D11 | Narrative: phase1_requirements | `data/narrative/phase1_requirements.md` | Phase 1 requirements content |
| D12 | Narrative: phase1_acceptance | `data/narrative/phase1_acceptance.md` | Phase 1 acceptance criteria content |
| D13 | Narrative: phase2_architecture | `data/narrative/phase2_architecture.md` | Phase 2 architecture content |
| D14 | Narrative: phase2_technology | `data/narrative/phase2_technology.md` | Phase 2 technology content |
| D15 | Narrative: phase2_testing | `data/narrative/phase2_testing.md` | Phase 2 testing strategy content |
| D16 | Narrative: phase3_intro | `data/narrative/phase3_intro.md` | Phase 3 intro content |
| D17 | Narrative: phase4_intro | `data/narrative/phase4_intro.md` | Phase 4 intro content |
| D18 | Narrative: phase5_intro | `data/narrative/phase5_intro.md` | Phase 5 intro content |
| D19 | Narrative: governance_intro | `data/narrative/governance_intro.md` | Governance page content |
| D20 | Explanations (9 files) | `data/explanations/*.md` | Test type explanations: unit, integration, e2e, acceptance, ai_evals, security, performance, steelthread, ai_acceptance |
| D21 | Design system CSS | `static/css/design-system.css` | BEM-convention CSS: layout, cards, nav, phase styles, annotations |
| D22 | Governance CSS | `static/css/governance.css` | Governance dashboard-specific styles |
| D23 | Syntax theme CSS | `static/css/syntax-themes.css` | Pygments syntax highlighting styles |
| D24 | Viewer JS | `static/js/viewer.js` | Test runner, trace inspector, ask form client-side logic |
| D25 | Line selection JS | `static/js/line_selection.js` | Code canvas line selection behavior |
| D26 | Live traces JS | `static/js/live_traces.js` | Real-time trace monitoring client-side logic |
| D27 | Config | `config.py` | Centralized settings: API keys, thresholds, paths, DB URL |

## Component Templates

| Component | File | Macro | Parameters |
|-----------|------|-------|------------|
| Collapsible | `templates/components/collapsible.html` | `collapsible()` | `title, content, open=False, id=None` |
| Code Canvas | `templates/components/code_canvas.html` | `code_canvas()` | `code, filename, test_type, runnable, test_id, result, secondary, show_line_numbers, file_path` |
| Annotation Display | `templates/components/annotation_display.html` | `annotated_text()` | `text, annotations` |
| Annotation Display | `templates/components/annotation_display.html` | `render_annotation()` | `text, annotation, marker` |
| Rainbow Arc | `templates/components/rainbow_arc.html` | `rainbow_arc()` | `phases, url_for` |
| Phase Nav | `templates/components/phase_nav.html` | (include) | Uses `phase_order`, `phases`, `phase` from context |
| Artifact Card | `templates/components/artifact_card.html` | (include) | Uses context variables |

## Wiring

Key connections between affordances:

| Source | Connection | Target | Description |
|--------|-----------|--------|-------------|
| N1 `create_app()` | registers | N47, N48, N49, N45, N46 | Registers all 5 blueprints with URL prefixes |
| N1 `create_app()` | calls | N3 `setup_database_session()` | Initializes DB session lifecycle hooks |
| N3 `setup_database_session()` | creates | N37 `TSRRepository` | Instantiates repository per-request in `before_request` |
| N3 `setup_database_session()` | calls | N43 `init_tsr_api()`, N44 `init_governance()` | Injects repository into blueprint globals |
| N50 `ask_route()` | calls | N12 `sanitize_input()` → N4 `ask()` | Sanitizes then routes to version handler |
| N4 `ask()` | calls | N5/N6/N7 `ask_v{1,2,3}()` | Dispatches by version string |
| N7 `ask_v3()` | calls | N9 `get_relevant_docs()` | RAG retrieval before Claude API call |
| N9 `get_relevant_docs()` | reads | D1-D4 via N11 `get_collection()` | Queries ChromaDB for relevant knowledge base docs |
| N5/N6/N7 | calls | N8 `get_client()` | Gets/creates Anthropic client |
| N5/N6/N7 | calls | N15 `convert_markdown_to_html()`, N13 `format_response()` | Formats output |
| N47 phase routes | calls | N18 `load_narrative_content()` | Loads markdown from `data/narrative/` |
| N47 phase routes | calls | N19 `get_phase_context()` | Builds navigation context from N16 `PHASES` |
| N47 `phase_3()` | calls | N20, N21, N22, N24, N34 | Test navigator + syntax highlighting |
| N47 `phase_4()` | calls | N25, N26, N27, N32, N33, N30, N31 | Trace inspector + timeline + failure modes |
| N49 `test_navigator()` | calls | N20, N21, N22, N24, N34 | Same test navigator functions as Phase 3 |
| N49 `trace_inspector()` | calls | N25, N26, N27 | Same trace functions as Phase 4 |
| N51 `run_test()` | reads | N21 `get_test_path()` | Gets file path then runs pytest subprocess |
| N46 `dashboard()` | calls | N37 `.query()`, `.count()` | Fetches TSR list and statistics |
| N45 `create_tsr()` | calls | N38 `GoNoGoEvaluator.apply_decision()` → N37 `.save()` | Evaluates rules then persists |
| U1 phase_nav | reads | N16 `PHASES`, N17 `PHASE_ORDER` | Renders navigation from phase config |
| U3 card grid | reads | N23 `TEST_TYPES`, N22 explanations | Displays test type cards with descriptions |
| U4 code_canvas | reads | N34 `syntax_highlight()` output | Renders highlighted code |
| U6 trace sidebar | reads | N25 `get_traces_by_version()` | Lists traces for selected version |
| U7 annotation markers | reads | N27 `render_annotated_response()` | Injects annotation spans into response text |

## Blueprints Summary

| Blueprint | Variable | Module | Prefix | Routes |
|-----------|----------|--------|--------|--------|
| narrative | `narrative_bp` | `viewer/narrative.py` | `(root)` | `/`, `/problem`, `/phase/{1-5}`, `/governance` |
| app | `app_bp` | `app/routes.py` | `(root)` | `/ask` |
| viewer | `viewer_bp` | `viewer/routes.py` | `/viewer` | `/tests`, `/traces`, `/timeline`, `/tests/run/<id>` |
| tsr_api | `tsr_api` | `tsr/api.py` | `/api/tsr` | CRUD + query + stats + approve |
| governance | `governance` | `viewer/governance.py` | `/governance` | `/dashboard`, `/tsr/<id>`, `/tsr/<id>/approve`, `/compare` |

## Test Suite

| Directory | Type | Key Tests |
|-----------|------|-----------|
| `tests/unit/` | Unit | `test_sanitize`, `test_tokens`, `test_format` |
| `tests/integration/` | Integration | `test_chroma`, `test_ai_service`, `test_rag_pipeline` |
| `tests/e2e/` | E2E | `test_ask_flow`, `test_versions` |
| `tests/acceptance/` | Acceptance | `test_user_ask`, `test_response` |
| `tests/evals/` | AI Evals | `eval_v1_length`, `eval_v2_accuracy`, `eval_v3_grounding` |
| `tests/security/` | Security | `test_validation`, `test_injection` |
| `tests/performance/` | Performance | `test_token_usage` |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/deploy.sh` | Build, push, deploy Docker image to ECS |
| `scripts/verify-deployment.sh` | Smoke test deployed endpoints |
| `scripts/generate_traces.py` | Generate 60 trace records (20 per version) |
| `scripts/generate_tsr.py` | Generate sample TSR data |
| `scripts/init_database.py` | Initialize PostgreSQL schema |
| `scripts/seed_test_data.py` | Seed development test data |
| `scripts/init_monitoring_baselines.py` | Initialize monitoring baseline metrics |
