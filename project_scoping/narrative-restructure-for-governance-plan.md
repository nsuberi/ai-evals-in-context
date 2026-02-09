# Plan: Narrative Restructure for Governance-First Framing

## Context

The app's narrative flow currently frames the journey as "Idea → Production → Monitoring" with test tools and trace inspection as the centerpiece. The desired state reframes the entire journey around **governance as an accelerator**: governance process visibility from the homepage, test types as the core narrative (not code viewing), and a richer trace-based iteration viewer in Phase 4.

This plan bridges the current state to the desired state described in `project_scoping/narrative-restructure-for-governance-plan.md`.

---

## Desired-State Breadboard

### Places (Δ from Current State)

| ID | Place | Status | Route | What Changes |
|----|-------|--------|-------|-------------|
| P1 | Landing Page | **MODIFY** | `/` | Hero → governance-first messaging; 3-part cycle → Governance/Approvals/Business Value; add guiding principle quote; add rainbow arc phase visual with P5→P1 feedback loop |
| P2 | Problem Statement | unchanged | `/problem` | — |
| P3 | Phase 1 | **RENAME** | `/phase/1` | "Interviewing to Discover Requirements" |
| P4 | Phase 2 | **RENAME** | `/phase/2` | "Planning a Solution Design" |
| P5 | Phase 3 | **RESTRUCTURE** | `/phase/3` | "Building with AI"; test type explanations become center stage cards; code canvas/run button move to inline collapsible |
| P6 | Phase 4 | **ENHANCE** | `/phase/4` | "Building AI Features"; add failure mode summaries per version; add architecture context; expand to ~20 traces per version |
| P7 | Phase 5 | **MODIFY** | `/phase/5` | "Continuous Monitoring"; add feedback loop visual linking back to P3 |
| P8 | Governance Overview | unchanged | `/governance` | — |
| P9-P15 | TSR + Standalone views | unchanged | various | — (backward compat) |

### UI Affordances (Δ from Current State)

| ID | Affordance | Location | Status | Description |
|----|-----------|----------|--------|-------------|
| U3 | Three-Part Framework cards | P1 | **MODIFY** | Replace "Idea/Production/Monitoring" with "Governance/Approvals/Business Value Assessment" |
| U41 | Guiding Principle banner | P1 | **NEW** | Blockquote: "Experimentation is the path to production, governance is the gate..." |
| U42 | Rainbow arc phase visual | P1 | **NEW** | Eye-shaped ("ojo") arc showing phases 1-5, arrow from P5 back to P1, clickable nodes |
| U43 | Test type narrative cards | P5 | **NEW** | Full-width card grid showing explanation content per test type, AI acceptance prominent first |
| U44 | Code collapsible per type | P5 | **NEW** | Inline collapsible under each card: test file list + code canvas + run button + app code |
| U45 | Failure mode summary panel | P6 | **NEW** | Per-version panel listing discovered failure modes with severity + resolution |
| U46 | Architecture context collapsible | P6 | **NEW** | Per-version collapsible showing prompt strategy and architecture decisions |
| U47 | Scrollable expanded trace list | P6 | **MODIFY** | Sidebar trace list expanded from 2-3 to ~20 items with scroll container |
| U48 | Feedback loop link | P7 | **NEW** | Visual section at bottom linking back to Phase 1: Discovery |
| U8 | Test type sidebar | P5 | **REMOVE** | Replaced by U43 test type cards (sidebar no longer primary navigation) |
| U10 | Individual test links | P5 | **MOVE** | Moved inside U44 collapsible (still functional, just nested) |
| U11 | Run Test button | P5 | **MOVE** | Moved inside U44 collapsible (still functional, just nested) |
| U12 | Code canvas (test) | P5 | **MOVE** | Moved inside U44 collapsible (still functional, just nested) |
| U13 | Code canvas (app) | P5 | **MOVE** | Moved inside U44 collapsible (still functional, just nested) |

All other UI affordances (U1-U2, U4-U7, U9, U14-U40) remain unchanged.

### Code Affordances (Δ from Current State)

| ID | Affordance | Status | Description |
|----|-----------|--------|-------------|
| N32 | `get_failure_modes(version)` | **NEW** | Returns failure mode list from FAILURE_MODES dict in `viewer/iteration_timeline.py` |
| N33 | `scripts/generate_traces.py` | **NEW** | Generates ~60 traces programmatically from knowledge base docs |

All other code affordances (N1-N31) remain unchanged and are reused.

### Wiring Changes

**P1 Landing (modified wiring):**
```
[U3 Three-Part Framework] (display: Governance, Approvals, Business Value)  ← was Idea/Production/Monitoring
[U41 Guiding Principle] (display only)                                      ← NEW
[U42 Rainbow arc] (clickable phases → P3/P4/P5/P6/P7; feedback arrow)      ← NEW
[U1 "Start the Journey" CTA] ──→ P2                                        ← unchanged
[U2 Phase overview cards] ──→ P3-P7 (updated titles)                       ← titles changed
```

**P5 Phase 3 "Building with AI" (restructured wiring):**
```
[U15 AI eval banner] (retained)
[U43 Test type cards] ◀──populates── get_explanation() for ALL types (N15)  ← NEW center stage
    Each card: type name, explanation content, "Relationship to AI"
    [click "View Code"] ──navigates──→ same page with ?test_type=X&show_code=1
[U44 Code collapsible] (shown when show_code=1)                             ← NEW (contains moved affordances)
    [U10 Test links] ──calls──→ N14 get_test_code()                        ← moved here
    [U12 Code canvas] ◀──populates── N14                                   ← moved here
    [U11 Run button] ──calls──→ N21 runTest()                              ← moved here
    [U13 App code canvas] ◀──populates── N14                               ← moved here
```

**P6 Phase 4 "Building AI Features" (enhanced wiring):**
```
[U22 Version timeline] (retained)
[U23 Comparison cards] (retained)
[U45 Failure mode panel] ◀──populates── N32 get_failure_modes(version)      ← NEW
[U46 Architecture context] (per-version, collapsible)                       ← NEW
[U16 Version tabs] ──calls──→ N16 get_traces_by_version() (now ~20 traces)
[U47 Expanded trace list] ◀──populates── N16 (scrollable, ~20 items)       ← MODIFIED
[U18-U21] (annotated response, footnotes, metadata, prompt — all retained)
```

**P7 Phase 5 "Continuous Monitoring" (added wiring):**
```
[U26-U28 Demo form, response, trace panel] (all retained)
[U48 Feedback loop link] ──→ P3 (Phase 1: Discovery)                       ← NEW
```

---

## Chunk 1: PHASES Config + Phase Nav Labels (Foundation)

**Goal:** Update all phase names/titles across the app. Every subsequent chunk depends on these names being correct.

**File:** `viewer/narrative.py` lines 20-101 — Update PHASES dict:

| Phase Key | Current Title | New Title | New Short Title |
|-----------|--------------|-----------|-----------------|
| `phase_1` | Interview & Requirements | Interviewing to Discover Requirements | Discovery |
| `phase_2` | Solution Design | Planning a Solution Design | Design |
| `phase_3` | Implementation | Building with AI | Build |
| `phase_4` | Pre-Production Evaluation | Building AI Features | Iterate |
| `phase_5` | Production Monitoring | Continuous Monitoring | Monitor |

Also update `subtitle` fields to match the new framing.

**File:** `templates/components/phase_nav.html` — No code changes needed (renders `p.short_title` from PHASES), but verify visually that new short titles fit the nav circles.

**Verification:** `pytest tests/e2e/test_narrative_flow.py -v` — all 19 tests should still pass (they check HTTP 200, not title text). Visit each phase and confirm the header and nav bar show updated names.

---

## Chunk 2: Landing Page Reframe — Governance as Center Stage

**Goal:** Replace "Idea → Production → Monitoring" framing with the governance-first three-part framework.

**File:** `templates/narrative/landing.html` — 3 sections to change:

### 2a. Hero section (lines 7-17)
Replace title and subtitle:
```
Current: "Follow Acme Widget Co's Journey" / "See how a real product team integrates AI evaluations..."
New:     "AI in Production: A Governance-First Approach" / Messaging about governance as accelerator
```

### 2b. Three-Part Cycle section (lines 23-48)
Replace the 3 cycle cards:
```
Current: Idea / Production / Monitoring
New:     Governance / Approvals / Business Value Assessment
```
- Card 1 "Governance": Getting things into production in a standardized way
- Card 2 "Approvals": Quality standards evaluation
- Card 3 "Business Value Assessment": "Is the juice worth the squeeze?"

Section title changes from "The Three-Part Development Cycle" to "The Three-Part Framework"

### 2c. Add guiding principle (new section after cycle cards, before phases)
```html
<section class="guiding-principle">
  <blockquote>
    "Experimentation is the path to production, governance is the gate
    to production, and business value is the lens through which you
    determine success."
  </blockquote>
</section>
```

### 2d. Phase overview cards (lines 54-91)
Update the 5 card titles and descriptions to match new phase names from Chunk 1.

### 2e. Rainbow arc phase visual (new component)
Add an eye-shaped ("ojo") arc visual showing phases 1-5 with a feedback arrow from Phase 5 back to Phase 1. This goes above or alongside the phase cards.

**New file:** `templates/components/rainbow_arc.html` — SVG/CSS arc with clickable phase nodes and a return arrow.

**File:** `static/css/design-system.css` — Append:
- `.guiding-principle` / `.guiding-principle blockquote` styling
- `.rainbow-arc` / `.rainbow-arc__phase` / `.rainbow-arc__feedback-arrow` styling

**Verification:** Visit `/` — hero shows governance messaging, 3 cards say Governance/Approvals/Business Value, guiding principle quote is visible, phase card names match Chunk 1, rainbow arc is rendered.

---

## Chunk 3: Phase 3 — Test Types as Center Stage

**Goal:** Restructure Phase 3 so test type *explanations* are the primary content and code viewing is secondary (in a collapsible or popup).

### Current layout (sidebar-primary):
```
[Sidebar: test type list + test file list] | [Main: code canvas + run button + explanation]
```

### Target layout (card-grid with secondary code):
```
[AI Eval Banner — retained]
[Grid of test type cards — each showing the explanation content]
  → clicking "View Code" on a card opens a collapsible/popup with code canvas + run button
```

**File:** `viewer/narrative.py` phase_3() (lines 200-248) — Modify to load explanations for ALL test types:
```python
all_type_explanations = {}
for t in TEST_TYPES:
    all_type_explanations[t['id']] = get_explanation(t['id'])
all_type_explanations['ai_acceptance'] = get_explanation('ai_acceptance')
```
Pass `all_type_explanations` to the template. Keep existing test_code loading for the popup/collapsible.

**File:** `templates/narrative/phase3_implementation.html` — Major restructure:
1. **Keep** the AI eval banner (lines 24-62) as-is
2. **Add** prominent statement: "AI evaluation is acceptance testing linked to business value"
3. **Replace** the `layout--sidebar` (lines 64-169) with a card grid:
   - AI Acceptance test types first (with AI badge)
   - Traditional test types in a grid below
   - Each card shows: type name, explanation content, "Relationship to AI" section, "View Code" button
4. **Add** a collapsible code section (reuse existing `collapsible` macro) that appears when "View Code" is clicked. Inside the collapsible:
   - Test file sidebar (test list within that type)
   - Code canvas with run button
   - Related app code canvas

**Approach (Collapsible, confirmed):** Use `?test_type=X&show_code=1` query parameter. When `show_code=1`, the page renders with the code section expanded for that test type as an inline collapsible beneath the card. This reuses the existing `collapsible` Jinja2 macro, requires no new JS, and is fully server-rendered matching existing patterns.

**File:** `static/css/design-system.css` — Append:
- `.test-type-cards` grid layout
- `.test-type-card` / `.test-type-card--ai` card styling
- `.test-type-card__view-code` button styling

**Existing utilities reused:**
- `get_explanation(type)` from `viewer/test_navigator.py` — already returns `{title, content, relationship_to_ai}`
- `get_tests_by_type(type)` — still used for the code section
- `get_test_code(test_id)` — still used for code display
- `syntax_highlight()` — still used for code rendering
- `collapsible` macro from `templates/components/collapsible.html`

**Verification:** Visit `/phase/3`:
- Test type cards are displayed in a grid
- AI acceptance tests are visually prominent
- Each card shows the explanation content from `data/explanations/*.md`
- Clicking "View Code" navigates to `/phase/3?test_type=unit&show_code=1` and shows the code section
- Run button works inside the code section
- No sidebar visible by default

---

## Chunk 4: Trace Data Expansion (Data Work)

**Goal:** Expand from 8 total traces to ~60 (20 per version) to support the richer Phase 4 viewer.

**Files to modify:**
- `data/traces/v1_traces.json` — expand from 2 to ~20 traces
- `data/traces/v2_traces.json` — expand from 3 to ~20 traces
- `data/traces/v3_traces.json` — expand from 3 to ~20 traces

**Schema:** Follow existing trace structure exactly:
```json
{
  "id": "v1-trace-NNN",
  "version": "v1",
  "question": "...",
  "prompt": "...",
  "response": "...",
  "latency_ms": NNN,
  "tokens": {"prompt": N, "completion": N},
  "sources": [],
  "annotations": [{"type": "...", "severity": "...", "text": "...", "span_start": N, "span_end": N}]
}
```

**Content requirements per version:**
- **v1:** All responses verbose (300+ words), `length_violation` + `prompt_issue` annotations
- **v2:** Concise (~80 words) but with `hallucination` annotations (wrong prices, specs, policies)
- **v3:** Concise, accurate, `accurate_answer` + `correct_retrieval` success annotations, sources populated

**Question topics (cover all 4 knowledge base docs):**
- Return policy (30-day window, $8.95 shipping, 5-7 business day refund)
- Pricing tiers (Basic $49, Pro $149, Enterprise $299)
- Product specs (Widget Pro X2 details)
- Shipping info (free over $50, international options)
- Plus variations: warranty, bulk orders, upgrades, cancellation, comparisons, etc.

**Data consistency constraint:** v2 hallucinations must be plausible-but-wrong (e.g., "$349" instead of "$299"), and v3 responses must exactly match `data/knowledge_base/` content.

**Approach (Programmatic, confirmed):** Write a Python generation script (`scripts/generate_traces.py`) that:
1. Reads the 4 knowledge base docs from `data/knowledge_base/`
2. Generates ~20 question/response pairs per version
3. Applies version-appropriate behavior (v1: verbose, v2: hallucinate, v3: grounded)
4. Calculates annotation span positions from response text
5. Writes to the trace JSON files

The script will use the knowledge base content as ground truth to ensure v2 hallucinations are plausible-but-wrong and v3 responses are accurate. It can be re-run if the knowledge base changes.

**Verification:** Run the script, then `python -c "import json; [print(f'{v}: {len(json.load(open(f\"data/traces/{v}_traces.json\")))} traces') for v in ['v1','v2','v3']]"` — should show ~20 each. Spot-check that v2 traces contain wrong facts and v3 traces match knowledge base docs.

---

## Chunk 5: Failure Modes + Architecture Context for Phase 4

**Goal:** Add failure mode summaries and architecture decision context per version.

### 5a. Backend: Add failure mode data

**File:** `viewer/iteration_timeline.py` — Add after line 34:
```python
FAILURE_MODES = {
    'v1': [
        {'id': 'fm-v1-01', 'name': 'Response too verbose', 'severity': 'warning',
         'description': 'Prompt asks for 300+ words, users want ~80',
         'resolution': 'Updated prompt constraints in v2'},
        {'id': 'fm-v1-02', 'name': 'No source attribution', 'severity': 'warning',
         'description': 'Responses never cite knowledge base',
         'resolution': 'Added RAG pipeline in v3'},
    ],
    'v2': [
        {'id': 'fm-v2-01', 'name': 'Price hallucination', 'severity': 'error',
         'description': 'Fabricates pricing details', 'resolution': 'RAG grounding in v3'},
        {'id': 'fm-v2-02', 'name': 'Spec hallucination', 'severity': 'error',
         'description': 'Fabricates product specifications', 'resolution': 'Knowledge base retrieval in v3'},
        {'id': 'fm-v2-03', 'name': 'Policy hallucination', 'severity': 'error',
         'description': 'Wrong return/shipping details', 'resolution': 'RAG grounding in v3'},
    ],
    'v3': []  # No failure modes — passes all evals
}

def get_failure_modes(version: str) -> list:
    return FAILURE_MODES.get(version, [])
```

### 5b. Route handler: Pass failure modes to template

**File:** `viewer/narrative.py` line 14 — Update import:
```python
from .iteration_timeline import get_iteration_summary, get_comparison_data, get_failure_modes
```

**File:** `viewer/narrative.py` phase_4() (line 274) — Add:
```python
failure_modes = get_failure_modes(version)
```
Pass `failure_modes=failure_modes` to `render_template`.

### 5c. Template: Add failure mode panel and architecture context

**File:** `templates/narrative/phase4_evaluation.html` — Add two new sections between the comparison cards (line 58) and the trace inspector section (line 60):

1. **Failure Mode Panel:**
```html
{% if failure_modes %}
<div class="narrative-content">
  <div class="failure-mode-panel failure-mode-panel--{{ current_version }}">
    <h3>Discovered Failure Modes ({{ current_version | upper }})</h3>
    {% for fm in failure_modes %}
    <div class="failure-mode-item failure-mode-item--{{ fm.severity }}">
      <strong>{{ fm.name }}</strong>
      <p>{{ fm.description }}</p>
      <span class="failure-mode-item__resolution">Resolution: {{ fm.resolution }}</span>
    </div>
    {% endfor %}
  </div>
</div>
{% endif %}
```

2. **Architecture Context (collapsible):**
```html
<div class="narrative-content">
  <div class="collapsible">
    <!-- Per-version prompt strategy and architecture decisions -->
    <!-- v1: Direct Claude call, no RAG, verbose prompt -->
    <!-- v2: Updated prompt constraints, still no RAG -->
    <!-- v3: RAG pipeline with ChromaDB, grounded prompt -->
  </div>
</div>
```

### 5d. Handle expanded trace list in sidebar

The trace list sidebar (lines 84-106) will now show ~20 items. Add a scrollable container:
```html
<div class="sidebar" style="max-height: 400px; overflow-y: auto;">
```

**File:** `static/css/design-system.css` — Append failure mode panel styles:
- `.failure-mode-panel` with version-colored left border
- `.failure-mode-item` with severity-colored name
- `.failure-mode-item__resolution` in success color

**Verification:** Visit `/phase/4?version=v2` — failure modes panel shows 3 error items with resolution text. Architecture context collapsible works. Trace list shows ~20 traces (after Chunk 4). `/phase/4?version=v3` shows no failure modes.

---

## Chunk 6: Phase 5 Feedback Loop + Content Updates

**Goal:** Add visual feedback loop to Phase 5 and update markdown content files.

### 6a. Phase 5 feedback loop

**File:** `templates/narrative/phase5_monitoring.html` — Add before bottom navigation:
```html
<section class="narrative-content" style="text-align: center;">
  <div class="feedback-loop">
    <p>Monitoring feeds back into discovery. Production data surfaces new requirements.</p>
    <a href="{{ url_for('narrative.phase_1') }}" class="feedback-loop__link">
      &#x21ba; Back to Phase 1: Discovery
    </a>
  </div>
</section>
```

**File:** `static/css/design-system.css` — Append `.feedback-loop` styling.

### 6b. Update narrative markdown content

**Files to update:**
- `data/narrative/landing.md` — governance-first messaging
- `data/narrative/phase3_intro.md` — "Building with AI" framing, test types as core narrative
- `data/narrative/phase4_intro.md` — "Building AI Features" framing, iteration and failure mode discovery
- `data/narrative/phase5_intro.md` — "Continuous Monitoring" framing, feedback loop emphasis

**Files to create (if missing):**
- `data/narrative/phase1_interview.md`
- `data/narrative/phase1_requirements.md`
- `data/narrative/phase1_acceptance.md`
- `data/narrative/phase2_architecture.md`
- `data/narrative/phase2_technology.md`
- `data/narrative/phase2_testing.md`

**Verification:** Visit each phase, confirm intro content renders with updated framing.

---

## Chunk 7: Test Updates

**Goal:** Update E2E tests to validate the new content and structure.

**File:** `tests/e2e/test_narrative_flow.py` — Add assertions:
- Landing page contains governance-related text
- Phase 3 contains test type card structure
- Phase 4 contains failure mode content when version=v2

**Verification:** `pytest tests/e2e/test_narrative_flow.py -v` — all tests pass.

---

## Dependency Graph

```
Chunk 1 (PHASES config) ─────────────┬── Chunk 2 (Landing reframe)
                                      ├── Chunk 3 (Phase 3 restructure)
Chunk 4 (Trace data) ──────────┐     ├── Chunk 5 (Phase 4 enhancements)
                                └─────┤
                                      ├── Chunk 6 (Phase 5 + content)
                                      └── Chunk 7 (Tests) ← depends on all above
```

**Execution order:**
1. **Chunk 1** first (all others depend on it)
2. **Chunks 2, 3, 4** in parallel (independent of each other)
3. **Chunk 5** after Chunks 1 + 4 (needs failure modes + expanded traces)
4. **Chunk 6** after Chunk 1
5. **Chunk 7** last

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Trace data consistency (60 traces must match knowledge base) | HIGH | Write traces in batches per question topic across all 3 versions; validate span positions programmatically |
| Phase 3 restructure breaks Test Navigator functionality | MEDIUM | Keep all existing code affordances (N13, N14, N15, N21); only change the template layout and add `show_code` parameter |
| Rainbow arc visual is complex to implement well | LOW | Start with a simplified CSS arc; polish later. Phase cards already provide the primary navigation |
| Backward compatibility regression | LOW | Standalone viewer routes (`/viewer/*`) are untouched; existing tests check HTTP 200 |

---

## Critical Files Summary

| File | Chunk | Change Type |
|------|-------|-------------|
| `viewer/narrative.py` | 1, 3, 5 | Modify PHASES, phase_3() data loading, phase_4() failure modes |
| `templates/narrative/landing.html` | 2 | Rewrite hero, cycle cards, add guiding principle + arc |
| `templates/narrative/phase3_implementation.html` | 3 | Major restructure: sidebar → card grid + code collapsible |
| `templates/narrative/phase4_evaluation.html` | 5 | Add failure modes panel, architecture context, scrollable traces |
| `templates/narrative/phase5_monitoring.html` | 6 | Add feedback loop section |
| `viewer/iteration_timeline.py` | 5 | Add FAILURE_MODES data + get_failure_modes() |
| `data/traces/v{1,2,3}_traces.json` | 4 | Expand from 8 to ~60 traces |
| `static/css/design-system.css` | 2, 3, 5, 6 | New styles for guiding principle, arc, test type cards, failure modes, feedback loop |
| `templates/components/rainbow_arc.html` | 2 | New component |
| `data/narrative/*.md` | 6 | Update/create content files |
| `tests/e2e/test_narrative_flow.py` | 7 | Update assertions |

---

## End-to-End Verification

After all chunks are complete:

```bash
# 1. Run existing E2E tests
pytest tests/e2e/test_narrative_flow.py -v

# 2. Run full test suite
pytest tests/e2e/ -v

# 3. Manual walkthrough
python run.py
# Visit: / → /problem → /phase/1 → /phase/2 → /phase/3 → /phase/4 → /phase/5 → /governance
# At each phase verify: header title, nav bar labels, content matches new framing

# 4. Phase 3 specific: confirm card grid, "View Code" opens code section, run button works
# 5. Phase 4 specific: confirm failure modes panel at v2, ~20 traces in sidebar, architecture context
# 6. Phase 5 specific: confirm feedback loop link back to Phase 1
# 7. Backward compat: visit /viewer/tests, /viewer/traces, /ask — all still work
```
