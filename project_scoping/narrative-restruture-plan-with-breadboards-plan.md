# AI Evals in Context: Narrative Restructure Plan

## Executive Summary

Transform the current tool-centric Flask application into a **linear narrative educational journey** following Acme Widget Co's journey from idea to production, with AI evals integrated alongside traditional testing.

**Source**: Breadboard at `/Users/nathansuberi/Downloads/ai-evals-breadboard.md`
**Codebase**: `/Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource`

---

# PART 1: BREADBOARD ANALYSIS OF EXISTING SITE

## 1.1 Current Places (Pages/Views)

### Demo Page (`/ask`)
- **Purpose**: Interactive chatbot demonstration
- **Affordances**:
  - Text input for questions
  - Version selector (v1/v2/v3)
  - Submit button
  - Response display with markdown rendering
  - Knowledge base pipeline trace display
- **Data**: Uses `app/ai_service.py` (v1/v2/v3 implementations), `app/rag.py` (Chroma vector store)

### Test Navigator (`/viewer/tests`, `/viewer/tests/<test_type>`)
- **Purpose**: Browse and explore test suite by type
- **Affordances**:
  - Sidebar navigation by test type (unit, integration, e2e, acceptance, evals, security, performance, steelthread, ai_acceptance)
  - Test list within selected type
  - Code canvas showing test code (primary) and related app code (secondary)
  - Test explanation panel (markdown)
  - Run test button (POST to `/viewer/tests/run/<test_id>`)
- **Data**: `viewer/test_navigator.py`, `data/explanations/*.md`, `tests/*/*.py`

### Trace Inspector (`/viewer/traces`, `/viewer/traces/<version>`)
- **Purpose**: Examine AI response traces with annotations
- **Affordances**:
  - Version selector (v1/v2/v3)
  - Trace list for selected version
  - Trace detail display (question, prompt, response, tokens, latency)
  - Annotated response with highlighted spans
  - Annotation legend (error, warning, success, info)
- **Data**: `viewer/trace_inspector.py`, `data/traces/{version}_traces.json`

### Iteration Timeline (`/viewer/timeline`)
- **Purpose**: Compare versions and view improvement metrics
- **Affordances**:
  - Version comparison cards (v1, v2, v3)
  - Metrics table (response length, KB usage, accuracy, latency)
  - Failure mode identification per version
  - Fixes applied narrative
- **Data**: `viewer/iteration_timeline.py`

### Governance Dashboard (`/governance/dashboard`)
- **Purpose**: TSR (Test Summary Report) management and approval
- **Affordances**:
  - TSR list with filtering (environment, decision status)
  - Statistics panel (go rate, pending approvals)
  - TSR detail view (`/governance/tsr/<id>`)
  - Approval action (`/governance/tsr/<id>/approve`)
  - TSR comparison (`/governance/compare`)
- **Data**: `viewer/governance.py`, `tsr/` module (database, repository, rules)

## 1.2 Current Navigation Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [Test Navigator]  [Trace Inspector]  [Iteration Timeline]  [Try Demo] │
└─────────────────────────────────────────────────────────────────────────┘
```

- **Pattern**: Horizontal tabs, tool-centric organization
- **Flow**: Non-linear - users jump between tools
- **Problem**: No narrative progression, no educational journey context

## 1.3 Current Wiring Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    BASE NAVIGATION (base.html)                 │
│                                                                │
│   Test Navigator ─── Trace Inspector ─── Timeline ─── Demo    │
│        │                    │               │          │       │
│        │                    │               │          │       │
│   ┌────▼────┐          ┌────▼────┐    ┌────▼────┐  ┌──▼──┐   │
│   │ tests/  │          │ traces/ │    │timeline/│  │/ask │   │
│   │ unit    │          │ v1      │    │         │  │     │   │
│   │ integ   │          │ v2      │    │ compare │  │ v1  │   │
│   │ e2e     │          │ v3      │    │ metrics │  │ v2  │   │
│   │ accept  │          │         │    │         │  │ v3  │   │
│   │ evals   │          │annotate │    │         │  │     │   │
│   │ security│          └─────────┘    └─────────┘  └─────┘   │
│   │ perf    │                                                 │
│   │ steel   │              ┌─────────────────────┐            │
│   │ ai_acc  │              │  GOVERNANCE         │            │
│   └─────────┘              │  (separate nav)     │            │
│                            │  dashboard → detail │            │
│                            │  → approve          │            │
│                            └─────────────────────┘            │
└────────────────────────────────────────────────────────────────┘
```

## 1.4 Existing Backend Components

| Component | File | Purpose |
|-----------|------|---------|
| AI Service | `app/ai_service.py` | v1/v2/v3 chatbot implementations with different prompts |
| RAG Pipeline | `app/rag.py` | Chroma vector store, document retrieval, embedding |
| Utilities | `app/utils.py` | Input sanitization, token counting, formatting |
| Test Navigator | `viewer/test_navigator.py` | Test discovery, explanation loading |
| Trace Inspector | `viewer/trace_inspector.py` | Trace loading, annotation rendering |
| Iteration Timeline | `viewer/iteration_timeline.py` | Version metrics, comparison data |
| Highlighting | `viewer/highlighting.py` | Syntax highlighting for code display |
| Governance | `viewer/governance.py` | TSR routes and approval workflow |
| TSR Module | `tsr/` | Database, repository, rules engine, API |

## 1.5 Existing Data/Content

| Directory | Content |
|-----------|---------|
| `data/knowledge_base/` | Acme Widget docs: pricing_tiers.md, product_specs.md, return_policy.md, shipping_info.md |
| `data/traces/` | Pre-generated traces: v1_traces.json, v2_traces.json, v3_traces.json |
| `data/explanations/` | Test type explanations: unit.md, integration.md, e2e.md, acceptance.md, ai_evals.md, security.md, performance.md, steelthread.md, ai_acceptance.md |
| `tests/` | Test suite: unit/, integration/, e2e/, acceptance/, evals/, security/, performance/, steelthread/, ai_acceptance/ |

---

# PART 2: TARGET STATE BREADBOARD

## 2.1 Rough Concept

**Core Purpose:** Educational journey showing how AI systems go from idea → production → monitoring, with AI evals integrated alongside traditional testing.

**User Journey:** Linear walkthrough with branch points, showing real code, real traces, real decisions.

**Key Innovation:** Not just explaining AI evals abstractly, but showing them in the context of a complete product development lifecycle with actual artifacts at each phase.

## 2.2 Target Places (Pages/Views)

### Landing Page (`/`)
- Introduces 3-part cycle: Idea → Production → Monitoring
- Shows 5 phases overview
- Sets expectation: "Follow Acme Widget Co's journey"
- **Key Artifact**: None (entry point)

### Problem Statement (`/problem`)
- Acme's business problem (churn, conversion)
- Metrics: customers leaving, can't find answers
- Proposed solution: Interactive chatbot
- **Key Artifact**: Business case summary

### Phase 1: Interview & Requirements (`/phase/1`)
- Interview transcript/notes
- Requirements extraction
- Acceptance criteria defined
- **Key Artifact**: Requirements doc

### Phase 2: Solution Design (`/phase/2`)
- Architecture diagram (chatbot + knowledge base + web integration)
- Technology choices
- Testing strategy diagram (where AI evals fit)
- **Key Artifact**: Design doc

### Phase 3: Implementation (`/phase/3`)
- Code walkthrough (simplified but real)
- Traditional test suite (unit/integration/e2e)
- CI/CD pipeline
- **Key Artifact**: Test pyramid diagram

### Phase 4: Pre-Production Evaluation (`/phase/4`)
- **Version Comparison View:**
  - v1 (too verbose)
  - v2 (doesn't use KB effectively)
  - v3 (concise + KB)
- For each version:
  - Prompt display
  - Architecture changes
  - 5 sample traces with annotations
- Failure mode identification
- **Key Artifact**: Evaluation report

### Phase 5: Production Monitoring (`/phase/5`)
- **Live Demo Section:**
  - Interactive chatbot (ask the refund question)
  - Live trace generation
- **Production Trace Viewer:**
  - Accumulating traces over time
  - Traditional metrics (response time, errors)
  - AI-specific metrics (KB usage, answer quality)
- **Key Artifact**: Monitoring dashboard

### Governance View (`/governance`)
- Cross-phase summary
- Failure modes identified → resolved
- Version history with rationale
- Compliance audit trail
- **Key Artifact**: Governance report

## 2.3 Target Affordances

### Navigation Affordances
- **Next Phase** button (linear progression)
- **Phase Selector** (jump to specific phase)
- **Back to Overview** (return to landing)

### Phase 1 Affordances
- Read interview transcript
- Highlight key requirements
- See extracted acceptance criteria

### Phase 2 Affordances
- View architecture diagram (interactive SVG?)
- Toggle between "full architecture" and "testing strategy" views
- See technology rationale

### Phase 3 Affordances
- View code tabs (chatbot.py, knowledge_base.py, tests/)
- Run tests (simulated or real?)
- See test coverage report
- **REUSES**: Existing Test Navigator content

### Phase 4 Affordances
- **Version selector:** v1 | v2 | v3
- **For each version:**
  - View prompt (collapsible)
  - View architecture diff (what changed)
  - Browse 5 traces:
    - Trace 1: [scenario description]
    - Trace 2: [scenario description]
    - etc.
  - See annotations: "❌ Too verbose" → "✓ Fixed in v2"
- **Compare mode:** Side-by-side v1 vs v3
- **REUSES**: Existing Trace Inspector + Iteration Timeline

### Phase 5 Affordances
- **Live Demo:**
  - Text input: "What is your refund policy?"
  - Submit button
  - See real-time trace generation
  - View trace details (steps, KB lookups, response)
- **Production Trace List:**
  - Filter by date/time
  - Search by query
  - Sort by response time
- **Metrics Dashboard:**
  - Response time chart
  - KB hit rate
  - User satisfaction (if available)
- **REUSES**: Existing Demo page

### Governance Affordances
- Filter by version (v1/v2/v3)
- Filter by phase (pre-prod/production)
- Export audit report (PDF?)
- View failure mode timeline
- **REUSES**: Existing Governance Dashboard

## 2.4 Target Wiring Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         LANDING PAGE                            │
│  [3-Part Cycle] → [5 Phases] → [Start Journey]                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PROBLEM STATEMENT                           │
│  Business Context → Metrics → Proposed Solution                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: INTERVIEW & REQUIREMENTS                             │
│                                                                 │
│  Input: None (starting point)                                  │
│  Process: Read transcript → Extract requirements               │
│  Output: requirements.md → PHASE 2                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: SOLUTION DESIGN                                      │
│                                                                 │
│  Input: requirements.md                                         │
│  Process: Design architecture → Choose tech → Plan testing     │
│  Output: architecture.svg, design.md → PHASE 3                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: IMPLEMENTATION                                       │
│                                                                 │
│  Input: design.md                                               │
│  Process: Write code → Write tests → Run CI/CD                 │
│  Components:                                                    │
│    - chatbot_service.py (implementation)                       │
│    - tests/ (traditional test suite)                           │
│  Output: Working chatbot → PHASE 4                             │
│                                                                 │
│  ═══════════════════════════════════════════════════════════   │
│  INTEGRATES: Test Navigator (existing)                         │
│  ═══════════════════════════════════════════════════════════   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4: PRE-PRODUCTION EVALUATION                            │
│                                                                 │
│  Input: Working chatbot (v1 initial)                           │
│  Process: Generate traces → Identify failures → Iterate        │
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   VERSION 1  │ ───> │   VERSION 2  │ ───> │   VERSION 3  │ │
│  │              │      │              │      │              │ │
│  │ Prompt v1    │      │ Prompt v2    │      │ Prompt v3    │ │
│  │ No KB        │      │ Basic KB     │      │ Full KB      │ │
│  │ 5 traces     │      │ 5 traces     │      │ 5 traces     │ │
│  │ ❌ Too verbose│      │ ❌ KB misuse │      │ ✓ Good!      │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│                                                                 │
│  Output: Approved v3 → PHASE 5                                 │
│                                                                 │
│  ═══════════════════════════════════════════════════════════   │
│  INTEGRATES: Trace Inspector + Iteration Timeline (existing)   │
│  ═══════════════════════════════════════════════════════════   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 5: PRODUCTION MONITORING                                │
│                                                                 │
│  Input: Deployed v3 chatbot                                    │
│                                                                 │
│  ┌─────────────────────────┐      ┌─────────────────────────┐ │
│  │    LIVE DEMO            │      │  PRODUCTION TRACES      │ │
│  │                         │      │                         │ │
│  │  User Input ──────────> │      │  Accumulating over      │ │
│  │  "What's your refund    │      │  time as users          │ │
│  │   policy?"              │      │  interact with demo     │ │
│  │         │               │      │                         │ │
│  │         ▼               │      │  ┌───────────────────┐  │ │
│  │  chatbot_service.py     │      │  │ Trace 1 (user A)  │  │ │
│  │         │               │      │  │ Trace 2 (user B)  │  │ │
│  │         ▼               │      │  │ Trace 3 (user C)  │  │ │
│  │  trace_generator.py     │ ───> │  │ ...               │  │ │
│  │         │               │      │  └───────────────────┘  │ │
│  │         ▼               │      │                         │ │
│  │  Display trace          │      │  Filter/Search/Sort     │ │
│  └─────────────────────────┘      └─────────────────────────┘ │
│                                                                 │
│  ═══════════════════════════════════════════════════════════   │
│  INTEGRATES: Demo page (existing)                              │
│  ═══════════════════════════════════════════════════════════   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  GOVERNANCE VIEW                                               │
│                                                                 │
│  Aggregates data from ALL phases:                              │
│    - Phase 1: Requirements                                      │
│    - Phase 2: Design decisions                                  │
│    - Phase 4: v1→v2→v3 progression, failure modes              │
│    - Phase 5: Production traces                                 │
│                                                                 │
│  Output: Audit report showing:                                  │
│    - What was built vs what was required                        │
│    - How issues were identified and resolved                    │
│    - Current production behavior                                │
│                                                                 │
│  ═══════════════════════════════════════════════════════════   │
│  INTEGRATES: Governance Dashboard (existing)                   │
│  ═══════════════════════════════════════════════════════════   │
└─────────────────────────────────────────────────────────────────┘
```

## 2.5 Data Flow

### Phase 1 → Phase 2
- **Artifact:** `requirements.md`
- **Contains:** Acceptance criteria, functional requirements
- **Used by:** Design decisions in Phase 2

### Phase 2 → Phase 3
- **Artifact:** `design.md`, `architecture.svg`
- **Contains:** Architecture, tech stack, testing strategy
- **Used by:** Implementation and test writing

### Phase 3 → Phase 4
- **Artifact:** `chatbot_service.py` (v1 initial)
- **Contains:** Working chatbot, initial prompt
- **Used by:** Evaluation iterations

### Phase 4 → Phase 5
- **Artifact:** `chatbot_service.py` (v3 approved)
- **Contains:** Refined chatbot, optimized prompt, KB integration
- **Used by:** Production deployment

### Phase 5 → Governance
- **Artifact:** `production_traces.json`
- **Contains:** Real user interactions, metrics
- **Used by:** Compliance reporting, continuous improvement

---

# PART 3: FIT ANALYSIS - EXISTING TO TARGET

## 3.1 Component Mapping

| Target Place | Existing Component | Fit | Changes Needed |
|--------------|-------------------|-----|----------------|
| Landing | None | New | Create from scratch |
| Problem Statement | None | New | Create from scratch |
| Phase 1: Interview | None | New | Create content |
| Phase 2: Design | None | New | Create content + diagrams |
| Phase 3: Implementation | Test Navigator | **REUSE** | Wrap in phase context, add intro |
| Phase 4: Evaluation | Trace Inspector + Timeline | **REUSE** | Wrap in phase context, combine views |
| Phase 5: Monitoring | Demo Page | **REUSE** | Wrap in phase context, add metrics |
| Governance | Governance Dashboard | **REUSE** | Add cross-phase summary |

## 3.2 Content Gaps

### Must Create (New Content)

1. **Landing Page Content**
   - 3-part cycle explanation (Idea → Production → Monitoring)
   - 5 phases overview with descriptions
   - Hero messaging: "Follow Acme Widget Co's journey"

2. **Problem Statement Content**
   - Business problem narrative (40% churn, slow support)
   - Metrics dashboard mockup
   - Solution proposal (AI chatbot)
   - Success criteria (5s response, 95% accuracy, 80% deflection)

3. **Phase 1: Interview & Requirements**
   - Interview transcript (stakeholder conversation)
   - Requirements extraction document
   - Acceptance criteria list

4. **Phase 2: Solution Design**
   - Architecture diagram (SVG)
   - Technology choices rationale
   - Testing strategy diagram showing where AI evals fit

### Already Exists (Reuse)

1. **Phase 3 Content**: Test Navigator has all test code and explanations
2. **Phase 4 Content**: Traces exist with annotations, Timeline has metrics
3. **Phase 5 Content**: Demo fully functional, traces generated
4. **Governance Content**: TSR system with approval workflow

## 3.3 Navigation Transformation

**Current Navigation:**
```
[Test Navigator] [Trace Inspector] [Iteration Timeline] [Try Demo]
```

**Target Navigation:**
```
[Landing] [Problem] [Phase 1] [Phase 2] [Phase 3] [Phase 4] [Phase 5] [Governance]
```

**Mapping:**
- Test Navigator → Phase 3: Implementation
- Trace Inspector → Phase 4: Evaluation (part 1)
- Iteration Timeline → Phase 4: Evaluation (part 2)
- Try Demo → Phase 5: Monitoring

## 3.4 URL Structure Transformation

| Current URL | Target URL | Notes |
|-------------|------------|-------|
| `/` | `/` | Change from redirect to landing |
| `/ask` | `/phase/5` | Embed demo in Phase 5 |
| `/viewer/tests/*` | `/phase/3` | Embed Test Navigator in Phase 3 |
| `/viewer/traces/*` | `/phase/4` | Embed in Phase 4 |
| `/viewer/timeline` | `/phase/4` | Combine with traces |
| `/governance/*` | `/governance` | Keep, add cross-phase view |

**Backward Compatibility**: Keep `/viewer/*` routes working for direct links.

---

# PART 4: IMPLEMENTATION PLAN

## 4.1 Files to Create

### New Blueprint
```
viewer/narrative.py
```

### New Templates
```
templates/narrative/
├── base_narrative.html      # Extended base with phase navigation
├── landing.html             # Landing page
├── problem.html             # Problem statement
├── phase1_interview.html    # Interview & requirements
├── phase2_design.html       # Solution design
├── phase3_implementation.html  # Wraps test_navigator
├── phase4_evaluation.html   # Wraps trace_inspector + timeline
├── phase5_monitoring.html   # Wraps demo
└── governance_overview.html # Wraps governance dashboard

templates/components/
├── phase_nav.html           # Phase navigation bar
├── artifact_card.html       # Input/output artifact display
└── phase_progress.html      # Progress indicator
```

### New Content Files
```
data/narrative/
├── landing.md               # Landing page content
├── problem.md               # Business problem narrative
├── phase1_interview.md      # Interview transcript
├── phase1_requirements.md   # Requirements document
├── phase1_acceptance.md     # Acceptance criteria
├── phase2_architecture.md   # Architecture decisions
├── phase2_technology.md     # Tech stack rationale
├── phase2_testing.md        # Testing strategy
├── phase3_intro.md          # Implementation intro
├── phase4_intro.md          # Evaluation intro
├── phase5_intro.md          # Monitoring intro
└── governance_intro.md      # Governance intro
```

### New Visual Assets
```
static/images/diagrams/
├── idea-production-monitoring.svg  # 3-part cycle
├── five-phases-overview.svg        # Phase cards
├── architecture-diagram.svg        # System architecture
├── testing-pyramid.svg             # Test pyramid with AI evals
└── rag-pipeline.svg                # RAG architecture
```

## 4.2 Files to Modify

| File | Changes |
|------|---------|
| `app/__init__.py` | Register `narrative_bp` blueprint |
| `templates/base.html` | Update navigation to narrative flow |
| `app/routes.py` | Change `/` from redirect to landing |
| `static/css/design-system.css` | Add phase nav, artifact card, progress styles |

## 4.3 Implementation Sequence

### Step 1: Foundation (Blueprint + Base Template)
1. Create `viewer/narrative.py` with PHASES config and route handlers
2. Create `templates/narrative/base_narrative.html`
3. Create `templates/components/phase_nav.html`
4. Create `templates/components/artifact_card.html`
5. Register blueprint in `app/__init__.py`
6. Create `data/narrative/` directory structure
7. Add CSS for phase navigation

### Step 2: Landing + Problem
1. Create `templates/narrative/landing.html`
2. Create `templates/narrative/problem.html`
3. Write `data/narrative/landing.md`
4. Write `data/narrative/problem.md`
5. Create `static/images/diagrams/idea-production-monitoring.svg`
6. Create `static/images/diagrams/five-phases-overview.svg`

### Step 3: Phase 1 & 2 (New Content)
1. Create `templates/narrative/phase1_interview.html`
2. Create `templates/narrative/phase2_design.html`
3. Write interview transcript content
4. Write requirements and acceptance criteria
5. Write architecture and technology choices
6. Write testing strategy content
7. Create architecture diagram SVG
8. Create testing pyramid SVG

### Step 4: Phase 3 Integration
1. Create `templates/narrative/phase3_implementation.html`
2. Extract reusable content from `test_navigator.html` into include
3. Write `data/narrative/phase3_intro.md`
4. Wire up Test Navigator affordances within phase wrapper

### Step 5: Phase 4 Integration
1. Create `templates/narrative/phase4_evaluation.html`
2. Create tabbed interface for Trace Inspector vs Timeline views
3. Write `data/narrative/phase4_intro.md`
4. Add version comparison narrative wrapper

### Step 6: Phase 5 Integration
1. Create `templates/narrative/phase5_monitoring.html`
2. Embed demo functionality
3. Write `data/narrative/phase5_intro.md`
4. Add production trace context

### Step 7: Governance & Navigation Update
1. Create `templates/narrative/governance_overview.html`
2. Add cross-phase summary component
3. Update `templates/base.html` navigation
4. Update `app/routes.py` root route
5. Polish CSS transitions and progress indicator

## 4.4 Technical Decisions

### Template Composition Strategy
Phase templates use `{% include %}` to embed existing content:
```jinja2
{# phase3_implementation.html #}
{% extends "narrative/base_narrative.html" %}
{% block phase_content %}
  {% include "test_navigator_content.html" %}
{% endblock %}
```

This requires extracting content blocks from existing templates.

### Route Coexistence
Keep existing routes working:
- `/viewer/tests/*` → Still works
- `/viewer/traces/*` → Still works
- `/viewer/timeline` → Still works
- `/ask` → Still works

New routes layer on top:
- `/phase/3` → Embeds Test Navigator
- `/phase/4` → Embeds Trace Inspector + Timeline
- `/phase/5` → Embeds Demo

### URL Prefix Compatibility
Narrative blueprint respects `APPLICATION_ROOT` for CloudFront:
```python
app.register_blueprint(narrative_bp, url_prefix=combine_prefix(url_prefix, ''))
```

### State via Query Parameters
Deep linking supported:
- `/phase/3?test_type=evals&test=eval_v3_grounding`
- `/phase/4?version=v2&trace=v2-trace-001`
- `/phase/5?version=v3`

---

# PART 5: CONTENT SPECIFICATIONS

## 5.1 Landing Page Content

### Hero Section
```
Follow Acme Widget Co's Journey
From Idea to Production with AI Evals

See how a real product team integrates AI evaluations alongside
traditional testing through five development phases.
```

### 3-Part Cycle Explanation
1. **Idea**: Understanding the problem, defining requirements, designing the solution
2. **Production**: Building the code, writing tests, iterating on AI behavior
3. **Monitoring**: Deploying to production, observing real usage, governance and compliance

### 5 Phases Overview
| Phase | Name | Description |
|-------|------|-------------|
| 1 | Interview & Requirements | Understand stakeholder needs, extract requirements, define acceptance criteria |
| 2 | Solution Design | Design architecture, choose technology, plan testing strategy |
| 3 | Implementation | Write code, build test suite, set up CI/CD |
| 4 | Pre-Production Evaluation | Iterate on AI behavior through v1→v2→v3, identify and fix failure modes |
| 5 | Production Monitoring | Deploy, observe real usage, collect production traces |

### CTA
"Start the Journey" → Problem Statement

## 5.2 Problem Statement Content

### Business Problem
```
Acme Widget Co. is losing customers.

Their support team is overwhelmed with repetitive questions:
- "What's your return policy?"
- "How much does Enterprise cost?"
- "When will my order arrive?"

These questions all have answers in their documentation, but customers
don't want to search. They want instant answers.
```

### Current Metrics
- **40%** customer churn rate
- **24 hours** average response time
- **$500K** annual support cost
- **60%** of tickets are FAQ questions

### Proposed Solution
```
An AI-powered support chatbot that:
- Answers questions instantly
- Uses the company knowledge base
- Escalates complex issues to humans
```

### Success Criteria
| Metric | Target |
|--------|--------|
| Response time | < 5 seconds |
| Accuracy | > 95% on product questions |
| Deflection rate | > 80% of FAQ questions handled |
| Customer satisfaction | No decrease from current baseline |

## 5.3 Phase 1: Interview Transcript

### Stakeholder Interview
```
INTERVIEWER: What's the biggest pain point for your support team?

SARAH (Support Manager): We're drowning in repetitive questions. "What's your
return policy?" "How much does Enterprise cost?" These are all in our docs,
but customers don't want to search.

INTERVIEWER: How many of these repetitive questions do you see?

SARAH: About 60% of our tickets. My team spends hours answering the same
questions over and over. We could be solving real problems instead.

INTERVIEWER: What would success look like?

SARAH: If 80% of these simple questions could be answered instantly and
accurately, my team could focus on the complex issues that actually need
human judgment. Speed matters too - our customers expect instant answers now.

INTERVIEWER: What concerns do you have about an AI solution?

SARAH: Accuracy is everything. If it gives wrong information about pricing
or return policies, that's worse than slow human support. We need to be able
to trust what it says.

INTERVIEWER: How would you want to verify that trust?

SARAH: I'd want to see exactly where the AI is getting its information.
If it's pulling from our official docs, that's trustworthy. If it's just
making things up, that's a liability.
```

### Requirements Extraction
1. **Instant Response**: System must respond within 5 seconds
2. **Grounded Answers**: Responses must cite official knowledge base
3. **Accuracy**: Must accurately reflect pricing, policies, and product info
4. **Escalation Path**: Complex questions routed to human support
5. **Transparency**: Users should know they're talking to AI

### Acceptance Criteria
- [ ] Given a pricing question, the system responds with correct tier pricing from knowledge base
- [ ] Given a return policy question, the system cites the official 30-day policy
- [ ] Given a shipping question, the system provides accurate delivery timeframes
- [ ] Given an ambiguous question, the system asks for clarification or escalates
- [ ] Response time P95 < 5 seconds
- [ ] Source citation included in every response

## 5.4 Phase 2: Solution Design

### Architecture Overview
```
┌─────────────────────────────────────────────────────────────┐
│                     WEB INTERFACE                           │
│  Customer types question → Displays response + sources     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    CHATBOT SERVICE                          │
│  1. Receives question                                       │
│  2. Retrieves relevant documents from KB                    │
│  3. Constructs prompt with context                          │
│  4. Calls AI model                                          │
│  5. Returns response with sources                           │
└────────────────────────────┬────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                              ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│    KNOWLEDGE BASE        │    │       AI MODEL           │
│    (Chroma Vector DB)    │    │    (Claude Sonnet)       │
│                          │    │                          │
│  - pricing_tiers.md      │    │  - Concise responses     │
│  - product_specs.md      │    │  - Grounded in context   │
│  - return_policy.md      │    │  - Source attribution    │
│  - shipping_info.md      │    │                          │
└──────────────────────────┘    └──────────────────────────┘
```

### Technology Choices
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Vector Store | Chroma | Lightweight, local, no external deps |
| Embeddings | sentence-transformers | Fast, accurate, no API calls |
| AI Model | Claude Sonnet | Balance of quality and latency |
| Web Framework | Flask | Simple, Python native, easy testing |
| Knowledge Base | Markdown files | Version controlled, easy to update |

### Testing Strategy - Where AI Evals Fit
```
                    ┌─────────────────────────┐
                    │    AI ACCEPTANCE        │  ← AI Evals live here
                    │    - Grounding          │
                    │    - Accuracy           │
                    │    - No hallucination   │
                    └─────────────────────────┘
              ┌─────────────────────────────────────┐
              │         END-TO-END                  │
              │    - Full user journey              │
              │    - UI → API → Response            │
              └─────────────────────────────────────┘
        ┌───────────────────────────────────────────────────┐
        │              INTEGRATION                          │
        │    - RAG pipeline                                │
        │    - Vector store queries                        │
        │    - Prompt construction                         │
        └───────────────────────────────────────────────────┘
  ┌───────────────────────────────────────────────────────────────┐
  │                     UNIT                                      │
  │    - Input sanitization                                       │
  │    - Token counting                                           │
  │    - Response formatting                                      │
  └───────────────────────────────────────────────────────────────┘
```

**Key Insight**: AI Evals are acceptance tests for AI behavior. They sit at the top of the pyramid and validate that the AI system meets requirements like accuracy, grounding, and appropriate response format.

---

# PART 6: VERIFICATION PLAN

## 6.1 Navigation Flow Test
1. Visit `/` (Landing)
2. Click "Start Journey" → `/problem`
3. Click "Next Phase" → `/phase/1`
4. Click "Next Phase" → `/phase/2`
5. Click "Next Phase" → `/phase/3`
6. Click "Next Phase" → `/phase/4`
7. Click "Next Phase" → `/phase/5`
8. Click "Governance" → `/governance`
9. Verify phase indicator shows correct progress at each step

## 6.2 Content Rendering Test
1. Verify markdown content renders correctly in each phase
2. Verify diagrams load and display
3. Verify code syntax highlighting works in Phase 3

## 6.3 Component Integration Test
1. **Phase 3**: Test Navigator sidebar works, tests can be run
2. **Phase 4**: Trace Inspector version selection works, Timeline displays
3. **Phase 5**: Demo chat works, trace is generated
4. **Governance**: TSR list displays, filters work

## 6.4 Backward Compatibility Test
1. `/viewer/tests/unit` → Still works
2. `/viewer/traces/v1` → Still works
3. `/viewer/timeline` → Still works
4. `/ask` → Still works
5. `/governance/dashboard` → Still works

## 6.5 Proxy Support Test
```bash
APPLICATION_ROOT=/ai-evals python run.py
```
- All routes should work with `/ai-evals/` prefix
- Static assets load correctly
- Navigation links include prefix

## 6.6 Existing Test Suite
```bash
pytest tests/
```
- All existing tests should still pass

---

# PART 7: E2E AND STEEL THREAD TEST UPDATES

## 7.1 Current Test Structure

### E2E Tests (`tests/e2e/`)

**`test_ask_flow.py`** - Tests demo page interactions:
- `test_get_ask_page` - GET `/ask` returns demo page
- `test_post_question_v3` - POST with question returns grounded response
- `test_post_empty_question` - Empty question returns 400 error
- `test_version_selection` - v1/v2/v3 versions accepted

**`test_versions.py`** - Tests version behavior differences:
- `test_v1_is_verbose` - V1 produces >100 word responses
- `test_v2_is_concise` - V2 produces <150 word responses
- `test_v3_has_sources` - V3 includes RAG sources
- `test_v1_and_v2_have_no_sources` - V1/V2 have no sources
- `test_v3_uses_more_prompt_tokens` - V3 uses more tokens (RAG context)

### Steel Thread Tests (`tests/steelthread/`)

**`test_steel_thread.py`** - Playwright browser tests for deployed app:

**TestPortfolioEntry:**
- `test_portfolio_loads` - Portfolio homepage loads
- `test_accepting_ai_card_visible` - "Accepting AI" card visible
- `test_click_try_live_demo_navigates_to_app` - Demo link → `/ai-evals`

**TestFullJourney:**
- `test_full_journey_portfolio_to_viewer_tests` - Portfolio → `/viewer/tests`
- `test_health_endpoint_from_portfolio_journey` - Health check accessible
- `test_governance_dashboard_accessible` - `/governance/dashboard` loads
- `test_ask_page_form_elements` - `/ask` form elements present

**TestDeployedAppErrors:**
- `test_deployed_ask_endpoint_no_500` - POST `/ask` doesn't return 500
- `test_deployed_ask_returns_structured_response` - Returns JSON not exceptions
- `test_deployed_health_endpoint` - Health returns healthy
- `test_deployed_ask_form_submission` - Form submission works with prefix

## 7.2 Required Test Changes

### New E2E Tests to Add (`tests/e2e/test_narrative_flow.py`)

```python
"""
E2E Test: Narrative Flow

Tests the complete narrative educational journey through all phases.
"""
import pytest


class TestNarrativeNavigation:
    """Test suite for narrative navigation flow"""

    def test_landing_page_loads(self, client):
        """GET / should return landing page with 3-part cycle"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Acme Widget' in response.data or b'journey' in response.data.lower()

    def test_problem_page_loads(self, client):
        """GET /problem should return problem statement"""
        response = client.get('/problem')
        assert response.status_code == 200
        assert b'churn' in response.data.lower() or b'support' in response.data.lower()

    def test_phase_pages_load(self, client):
        """Each phase page should load successfully"""
        for phase in range(1, 6):
            response = client.get(f'/phase/{phase}')
            assert response.status_code == 200, f"Phase {phase} failed to load"

    def test_governance_page_loads(self, client):
        """GET /governance should return governance overview"""
        response = client.get('/governance')
        assert response.status_code == 200

    def test_next_phase_links_present(self, client):
        """Each phase should have Next Phase navigation"""
        for phase in range(1, 5):  # Phases 1-4 should have "next"
            response = client.get(f'/phase/{phase}')
            assert b'Next' in response.data or b'phase/' in response.data


class TestPhaseContent:
    """Test suite for phase-specific content"""

    def test_phase3_includes_test_navigator(self, client):
        """Phase 3 should include Test Navigator content"""
        response = client.get('/phase/3')
        assert response.status_code == 200
        # Should have test type references
        assert b'unit' in response.data.lower() or b'test' in response.data.lower()

    def test_phase4_includes_trace_content(self, client):
        """Phase 4 should include trace/evaluation content"""
        response = client.get('/phase/4')
        assert response.status_code == 200
        # Should have version references
        assert b'v1' in response.data.lower() or b'version' in response.data.lower()

    def test_phase5_includes_demo(self, client):
        """Phase 5 should include demo functionality"""
        response = client.get('/phase/5')
        assert response.status_code == 200
        # Should have input form or demo reference
        assert b'question' in response.data.lower() or b'demo' in response.data.lower()


class TestBackwardCompatibility:
    """Ensure old routes still work"""

    def test_viewer_tests_still_works(self, client):
        """Legacy /viewer/tests route should still work"""
        response = client.get('/viewer/tests')
        assert response.status_code == 200

    def test_viewer_traces_still_works(self, client):
        """Legacy /viewer/traces route should still work"""
        response = client.get('/viewer/traces')
        assert response.status_code == 200

    def test_viewer_timeline_still_works(self, client):
        """Legacy /viewer/timeline route should still work"""
        response = client.get('/viewer/timeline')
        assert response.status_code == 200

    def test_ask_still_works(self, client):
        """Legacy /ask route should still work"""
        response = client.get('/ask')
        assert response.status_code == 200
```

### New Steel Thread Tests to Add (`tests/steelthread/test_narrative_steel_thread.py`)

```python
"""Steel thread tests for narrative flow user journey.

These tests verify the complete educational journey from landing page
through all phases to governance, both locally and when deployed.
"""

import re
import pytest
from playwright.sync_api import Page, expect


# Deployed app base URL
DEPLOYED_APP_URL = "https://portfolio.cookinupideas.com/ai-evals"


class TestNarrativeJourneyLocal:
    """Tests for narrative flow with local/configured base URL."""

    def test_landing_page_has_start_journey(self, page: Page, base_url: str):
        """Landing page should have 'Start Journey' or similar CTA."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Look for journey/start CTA
        cta = page.locator("a, button", has_text=re.compile(r"start|journey|begin", re.I))
        expect(cta.first).to_be_visible(timeout=10000)

    def test_linear_navigation_through_phases(self, page: Page, base_url: str):
        """User can navigate linearly from landing through all phases."""
        # Start at landing
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Click to problem
        page.click("a:has-text('Start'), a:has-text('Journey'), a:has-text('Begin')")
        page.wait_for_url("**/problem**", timeout=10000)

        # Navigate through phases 1-5
        for phase in range(1, 6):
            # Click "Next Phase" or similar
            next_btn = page.locator("a, button", has_text=re.compile(r"next|phase.*" + str(phase + 1), re.I))
            if next_btn.count() > 0:
                next_btn.first.click()
                page.wait_for_url(f"**/phase/{phase + 1}**" if phase < 5 else "**/governance**", timeout=10000)

    def test_phase3_test_navigator_functional(self, page: Page, base_url: str):
        """Phase 3 Test Navigator should allow browsing tests."""
        page.goto(f"{base_url}/phase/3")
        page.wait_for_load_state("networkidle")

        # Should have test type sidebar or tabs
        test_types = page.locator("a, button", has_text=re.compile(r"unit|integration|e2e", re.I))
        expect(test_types.first).to_be_visible(timeout=10000)

    def test_phase4_version_selection(self, page: Page, base_url: str):
        """Phase 4 should allow selecting v1/v2/v3 versions."""
        page.goto(f"{base_url}/phase/4")
        page.wait_for_load_state("networkidle")

        # Should have version selectors
        versions = page.locator("a, button, [data-version]", has_text=re.compile(r"v[123]|version", re.I))
        expect(versions.first).to_be_visible(timeout=10000)

    def test_phase5_demo_functional(self, page: Page, base_url: str):
        """Phase 5 demo should have input form and submit."""
        page.goto(f"{base_url}/phase/5")
        page.wait_for_load_state("networkidle")

        # Should have input and submit
        text_input = page.locator("input[type='text'], textarea").first
        expect(text_input).to_be_visible(timeout=10000)

        submit = page.locator("button[type='submit'], button:has-text('Ask'), button:has-text('Submit')")
        expect(submit.first).to_be_visible(timeout=10000)


class TestDeployedNarrativeJourney:
    """Tests for deployed app narrative flow at portfolio.cookinupideas.com/ai-evals."""

    def test_deployed_landing_loads(self, page: Page):
        """Deployed landing page should load successfully."""
        page.goto(DEPLOYED_APP_URL)
        page.wait_for_load_state("networkidle")

        # Should not be error page
        expect(page.locator("body")).to_be_visible()
        content = page.content()
        assert "error" not in content.lower() or "acme" in content.lower()

    def test_deployed_problem_page(self, page: Page):
        """Deployed /problem page should load."""
        page.goto(f"{DEPLOYED_APP_URL}/problem")
        page.wait_for_load_state("networkidle")

        expect(page).to_have_url(re.compile(r".*/problem.*"))
        expect(page.locator("body")).to_be_visible()

    def test_deployed_all_phases_accessible(self, page: Page):
        """All phase pages should be accessible on deployed app."""
        for phase in range(1, 6):
            page.goto(f"{DEPLOYED_APP_URL}/phase/{phase}")
            page.wait_for_load_state("networkidle")

            assert page.url.endswith(f"/phase/{phase}") or f"/phase/{phase}" in page.url, \
                f"Phase {phase} URL mismatch: {page.url}"
            expect(page.locator("body")).to_be_visible()

    def test_deployed_governance_accessible(self, page: Page):
        """Governance overview should be accessible."""
        page.goto(f"{DEPLOYED_APP_URL}/governance")
        page.wait_for_load_state("networkidle")

        expect(page).to_have_url(re.compile(r".*/governance.*"))
        expect(page.locator("body")).to_be_visible()

    def test_deployed_backward_compatibility(self, page: Page):
        """Legacy routes should still work on deployed app."""
        legacy_routes = [
            "/viewer/tests",
            "/viewer/traces",
            "/viewer/timeline",
            "/ask",
            "/governance/dashboard"
        ]

        for route in legacy_routes:
            page.goto(f"{DEPLOYED_APP_URL}{route}")
            page.wait_for_load_state("networkidle")

            # Should not return error
            content = page.content()
            assert "404" not in content or "not found" not in content.lower(), \
                f"Legacy route {route} appears broken"

    def test_portfolio_to_narrative_journey(self, page: Page, portfolio_url: str):
        """Full journey: Portfolio → App Landing → Problem → Phase 1."""
        # Start at portfolio
        page.goto(portfolio_url)

        # Find and click the Accepting AI card
        card = page.locator(".group", has=page.locator("h3", has_text="Accepting AI"))
        demo_link = card.locator("a", has_text="Try Live Demo")
        expect(demo_link).to_be_visible(timeout=10000)
        demo_link.click()

        # Should land on new landing page (not /ask)
        page.wait_for_url("**/ai-evals/**", timeout=15000)

        # Should see landing page content
        expect(page.locator("body")).to_be_visible()

        # Navigate to problem
        start_link = page.locator("a, button", has_text=re.compile(r"start|journey|problem", re.I))
        if start_link.count() > 0:
            start_link.first.click()
            page.wait_for_url("**/problem**", timeout=10000)
```

### Updates to Existing Tests

**`tests/e2e/test_ask_flow.py`** - Keep existing tests (backward compatibility), no changes needed.

**`tests/steelthread/test_steel_thread.py`** - Keep existing tests, add import for new narrative tests.

**`tests/steelthread/conftest.py`** - Add base_url fixture:
```python
@pytest.fixture(scope="session")
def base_url(request):
    """Base URL from CLI option or default to local."""
    url = request.config.getoption("--base-url", default=None)
    if url:
        return url
    # Default to local dev server
    return "http://localhost:5000"
```

## 7.3 Test Execution Strategy

### Local Development Testing
```bash
# Run all tests including new narrative tests
pytest tests/

# Run only E2E tests
pytest tests/e2e/ -v

# Run only narrative flow tests
pytest tests/e2e/test_narrative_flow.py -v
```

### Local Steel Thread Testing (with local server)
```bash
# Start local server
python run.py &

# Run steel thread tests against local
pytest tests/steelthread/ --base-url=http://localhost:5000 -v
```

### Post-Deployment Verification
```bash
# Run steel thread tests against deployed app
pytest tests/steelthread/ --portfolio-url=https://portfolio.cookinupideas.com -v

# Run only narrative journey tests against deployed
pytest tests/steelthread/test_narrative_steel_thread.py -v
```

### CI/CD Integration
Add to GitHub Actions workflow:
```yaml
- name: Run E2E Tests
  run: pytest tests/e2e/ -v

- name: Run Steel Thread Tests (Post-Deploy)
  run: |
    pytest tests/steelthread/ \
      --portfolio-url=https://portfolio.cookinupideas.com \
      -v
```

## 7.4 Files to Create/Modify

### New Test Files
| File | Purpose |
|------|---------|
| `tests/e2e/test_narrative_flow.py` | E2E tests for narrative navigation and content |
| `tests/steelthread/test_narrative_steel_thread.py` | Playwright tests for deployed narrative flow |

### Modified Test Files
| File | Changes |
|------|---------|
| `tests/steelthread/conftest.py` | Add `base_url` fixture for local testing |

### Test Configuration Updates
| File | Changes |
|------|---------|
| `pytest.ini` or `pyproject.toml` | Ensure Playwright tests are properly configured |

## 7.5 Test Coverage Matrix

| Feature | E2E Test | Steel Thread (Local) | Steel Thread (Deployed) |
|---------|----------|---------------------|------------------------|
| Landing page loads | ✓ | ✓ | ✓ |
| Problem page loads | ✓ | ✓ | ✓ |
| Phase 1-5 pages load | ✓ | ✓ | ✓ |
| Governance page loads | ✓ | ✓ | ✓ |
| Linear navigation (Next buttons) | ✓ | ✓ | ✓ |
| Phase 3 Test Navigator works | ✓ | ✓ | ✓ |
| Phase 4 version selection | ✓ | ✓ | ✓ |
| Phase 5 demo functional | ✓ | ✓ | ✓ |
| Legacy routes backward compat | ✓ | ✓ | ✓ |
| Portfolio → App journey | - | - | ✓ |
| Health endpoint | - | ✓ | ✓ |
| Form prefix (CloudFront) | - | - | ✓ |

---

# PART 8: GIT WORKTREE PARALLELIZATION STRATEGY

## 8.1 Overview

This large refactor can be broken into **4 parallel work streams** using git worktrees. Each stream works on an independent branch in its own directory, reducing context bloat and allowing concurrent development.

```
ai-testing-resource/          # Main worktree (orchestration/integration)
├── .worktrees/
│   ├── wt-foundation/       # Worktree 1: Foundation (blueprint, base template)
│   ├── wt-content/          # Worktree 2: Content (markdown, diagrams)
│   ├── wt-templates/        # Worktree 3: Templates (phase templates)
│   └── wt-tests/            # Worktree 4: Tests (E2E, steel thread)
```

## 8.2 Work Stream Breakdown

### Stream 1: Foundation (MUST BE FIRST)
**Branch:** `feat/narrative-foundation`
**Worktree:** `.worktrees/wt-foundation`

**Scope:**
- Create `viewer/narrative.py` (blueprint with route handlers)
- Create `templates/narrative/base_narrative.html`
- Create `templates/components/phase_nav.html`
- Create `templates/components/artifact_card.html`
- Register blueprint in `app/__init__.py`
- Add CSS for phase navigation in `static/css/design-system.css`
- Create `data/narrative/` directory structure

**Dependencies:** None (start immediately)
**Blocks:** Streams 2, 3, 4 depend on this

**Files touched:**
```
viewer/narrative.py              (new)
templates/narrative/base_narrative.html  (new)
templates/components/phase_nav.html      (new)
templates/components/artifact_card.html  (new)
app/__init__.py                  (modify)
static/css/design-system.css     (modify)
data/narrative/                  (new directory)
```

### Stream 2: Content
**Branch:** `feat/narrative-content`
**Worktree:** `.worktrees/wt-content`

**Scope:**
- Write all markdown content files
- Create SVG diagrams
- No template or code changes

**Dependencies:** Stream 1 (for directory structure)
**Blocks:** Nothing (pure content)

**Files touched:**
```
data/narrative/landing.md            (new)
data/narrative/problem.md            (new)
data/narrative/phase1_interview.md   (new)
data/narrative/phase1_requirements.md (new)
data/narrative/phase1_acceptance.md  (new)
data/narrative/phase2_architecture.md (new)
data/narrative/phase2_technology.md  (new)
data/narrative/phase2_testing.md     (new)
data/narrative/phase3_intro.md       (new)
data/narrative/phase4_intro.md       (new)
data/narrative/phase5_intro.md       (new)
data/narrative/governance_intro.md   (new)
static/images/diagrams/idea-production-monitoring.svg  (new)
static/images/diagrams/five-phases-overview.svg        (new)
static/images/diagrams/architecture-diagram.svg        (new)
static/images/diagrams/testing-pyramid.svg             (new)
static/images/diagrams/rag-pipeline.svg                (new)
```

### Stream 3: Templates
**Branch:** `feat/narrative-templates`
**Worktree:** `.worktrees/wt-templates`

**Scope:**
- Create all phase-specific templates
- Modify base.html navigation
- Update app/routes.py root redirect

**Dependencies:** Stream 1 (for base_narrative.html, blueprint)
**Blocks:** Nothing

**Files touched:**
```
templates/narrative/landing.html             (new)
templates/narrative/problem.html             (new)
templates/narrative/phase1_interview.html    (new)
templates/narrative/phase2_design.html       (new)
templates/narrative/phase3_implementation.html (new)
templates/narrative/phase4_evaluation.html   (new)
templates/narrative/phase5_monitoring.html   (new)
templates/narrative/governance_overview.html (new)
templates/base.html                          (modify)
app/routes.py                                (modify)
```

### Stream 4: Tests
**Branch:** `feat/narrative-tests`
**Worktree:** `.worktrees/wt-tests`

**Scope:**
- Create new E2E tests for narrative flow
- Create new steel thread tests for narrative journey
- Update conftest.py with fixtures

**Dependencies:** Stream 1 (for route structure knowledge)
**Blocks:** Nothing (tests can be written against expected interface)

**Files touched:**
```
tests/e2e/test_narrative_flow.py             (new)
tests/steelthread/test_narrative_steel_thread.py (new)
tests/steelthread/conftest.py                (modify)
```

## 8.3 Execution Stages

### Stage 1: Foundation (Sequential)
```bash
# Create and switch to foundation branch
git checkout -b feat/narrative-foundation main

# Do foundation work (as described in Stream 1)
# ... implement blueprint, base template, CSS, etc ...

# Commit and push
git add -A
git commit -m "feat: add narrative blueprint foundation"
git push origin feat/narrative-foundation
```

**Duration:** Do this first, before setting up parallel worktrees

### Stage 2: Parallel Development (3 worktrees simultaneously)

After Stage 1 is complete, set up 3 parallel worktrees:

```bash
# Create worktrees branching from foundation
git worktree add .worktrees/wt-content -b feat/narrative-content feat/narrative-foundation
git worktree add .worktrees/wt-templates -b feat/narrative-templates feat/narrative-foundation
git worktree add .worktrees/wt-tests -b feat/narrative-tests feat/narrative-foundation
```

Now work can proceed in parallel in 3 separate directories:
- Terminal 1: `cd .worktrees/wt-content` → Work on content
- Terminal 2: `cd .worktrees/wt-templates` → Work on templates
- Terminal 3: `cd .worktrees/wt-tests` → Work on tests

### Stage 3: Integration (Merge in order)

```bash
# Return to main worktree
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource

# Create integration branch from foundation
git checkout -b feat/narrative-integration feat/narrative-foundation

# Merge content first (no conflicts expected)
git merge feat/narrative-content --no-ff -m "feat: add narrative content files"

# Merge templates (may need minor conflict resolution in base.html)
git merge feat/narrative-templates --no-ff -m "feat: add narrative phase templates"

# Merge tests last (no conflicts expected)
git merge feat/narrative-tests --no-ff -m "feat: add narrative E2E and steel thread tests"
```

### Stage 4: Cleanup

```bash
# Remove worktrees
git worktree remove .worktrees/wt-content
git worktree remove .worktrees/wt-templates
git worktree remove .worktrees/wt-tests

# Delete feature branches if desired
git branch -d feat/narrative-content
git branch -d feat/narrative-templates
git branch -d feat/narrative-tests
git branch -d feat/narrative-foundation
```

## 8.4 Worktree Commands Reference

### Setup Commands
```bash
# List all worktrees
git worktree list

# Add a new worktree with new branch
git worktree add <path> -b <branch-name> <start-point>

# Add worktree for existing branch
git worktree add <path> <existing-branch>

# Remove a worktree (after merging)
git worktree remove <path>
```

### Example: Full Setup Script
```bash
#!/bin/bash
# setup-narrative-worktrees.sh

# Ensure we're in the main repo
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource

# Create worktrees directory
mkdir -p .worktrees

# Foundation must be done first (manually or in main worktree)
echo "Stage 1: Complete foundation work in main worktree first"
echo "Branch: feat/narrative-foundation"
echo ""

# After foundation is complete, run:
echo "Stage 2: After foundation is done, run these commands:"
echo ""
echo "git worktree add .worktrees/wt-content -b feat/narrative-content feat/narrative-foundation"
echo "git worktree add .worktrees/wt-templates -b feat/narrative-templates feat/narrative-foundation"
echo "git worktree add .worktrees/wt-tests -b feat/narrative-tests feat/narrative-foundation"
```

### Example: Cleanup Script
```bash
#!/bin/bash
# cleanup-narrative-worktrees.sh

cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource

git worktree remove .worktrees/wt-content
git worktree remove .worktrees/wt-templates
git worktree remove .worktrees/wt-tests

rmdir .worktrees  # Only if empty
```

## 8.5 Conflict Prevention Strategy

### Files with Potential Conflicts

| File | Modified By | Resolution |
|------|-------------|------------|
| `app/__init__.py` | Foundation only | No conflict |
| `templates/base.html` | Foundation (adds CSS), Templates (changes nav) | Templates has full ownership |
| `static/css/design-system.css` | Foundation (adds classes) | Foundation only |
| `app/routes.py` | Templates only | No conflict |
| `tests/steelthread/conftest.py` | Tests only | No conflict |

### Interface Contract (Shared Understanding)

Before starting parallel work, document these contracts:

**Route Structure Contract:**
```python
NARRATIVE_ROUTES = {
    '/': 'narrative.landing',
    '/problem': 'narrative.problem',
    '/phase/1': 'narrative.phase_1',
    '/phase/2': 'narrative.phase_2',
    '/phase/3': 'narrative.phase_3',
    '/phase/4': 'narrative.phase_4',
    '/phase/5': 'narrative.phase_5',
    '/governance': 'narrative.governance_overview',
}
```

**Template Block Contract:**
```jinja2
{# All phase templates must define these blocks #}
{% block phase_header %}{% endblock %}
{% block phase_intro %}{% endblock %}
{% block phase_content %}{% endblock %}
{% block phase_navigation %}{% endblock %}
```

**Content File Contract:**
```
data/narrative/<name>.md
# Frontmatter (optional)
---
title: <title>
phase: <1-5 or 'landing'|'problem'|'governance'>
---
# Content in markdown
```

## 8.6 Timeline Estimate

| Stage | Work | Parallelism | Relative Effort |
|-------|------|-------------|-----------------|
| 1. Foundation | Blueprint, base template, CSS | Sequential | 1x |
| 2a. Content | Markdown, SVGs | Parallel | 1.5x |
| 2b. Templates | Phase templates, nav update | Parallel | 1.5x |
| 2c. Tests | E2E, steel thread tests | Parallel | 1x |
| 3. Integration | Merge, resolve conflicts | Sequential | 0.5x |
| 4. Verification | Run all tests, manual check | Sequential | 0.5x |

**Total work:** ~6x units
**Without parallelization:** ~6x elapsed time
**With parallelization (3 streams):** ~3x elapsed time (Foundation + max(Content,Templates,Tests) + Integration)

## 8.7 Claude Code Session Strategy

For each worktree, start a separate Claude Code session:

```bash
# Terminal 1: Content session
cd .worktrees/wt-content
claude

# Terminal 2: Templates session
cd .worktrees/wt-templates
claude

# Terminal 3: Tests session
cd .worktrees/wt-tests
claude
```

Each session has isolated context:
- Session 1: Only thinks about markdown content and diagrams
- Session 2: Only thinks about Jinja templates and HTML
- Session 3: Only thinks about pytest tests

This prevents context bloat from having all the work in a single session.

## 8.8 Orchestration Checklist

### Pre-Stage 1
- [ ] Ensure main branch is up to date: `git pull origin main`
- [ ] Create `.worktrees/` in `.gitignore`

### Stage 1: Foundation
- [ ] Create `feat/narrative-foundation` branch
- [ ] Implement: `viewer/narrative.py` (blueprint skeleton)
- [ ] Implement: `templates/narrative/base_narrative.html`
- [ ] Implement: `templates/components/phase_nav.html`
- [ ] Implement: `templates/components/artifact_card.html`
- [ ] Modify: `app/__init__.py` (register blueprint)
- [ ] Modify: `static/css/design-system.css` (add phase nav styles)
- [ ] Create: `data/narrative/` directory
- [ ] Commit and push foundation branch
- [ ] Verify foundation works: `python run.py` → visit `/` (should load base template)

### Stage 2: Parallel Work
- [ ] Create 3 worktrees from foundation
- [ ] Assign work to each worktree
- [ ] **Content worktree:** Write all `.md` files and create SVGs
- [ ] **Templates worktree:** Create all phase `.html` templates, update nav
- [ ] **Tests worktree:** Write E2E and steel thread tests
- [ ] Each worktree commits and pushes its branch

### Stage 3: Integration
- [ ] Create `feat/narrative-integration` from foundation
- [ ] Merge content: `git merge feat/narrative-content`
- [ ] Merge templates: `git merge feat/narrative-templates`
- [ ] Merge tests: `git merge feat/narrative-tests`
- [ ] Resolve any conflicts
- [ ] Push integration branch

### Stage 4: Verification
- [ ] Run E2E tests: `pytest tests/e2e/`
- [ ] Run steel thread tests locally: `pytest tests/steelthread/ --base-url=http://localhost:5000`
- [ ] Manual verification: Navigate through all phases
- [ ] Create PR for `feat/narrative-integration` → `main`

### Stage 5: Cleanup
- [ ] Merge PR to main
- [ ] Remove worktrees
- [ ] Delete feature branches
