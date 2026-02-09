# Plan: Landing Page Restructure, Phase Renames, Build Redesign, Governance Tab Overhaul

## Context

The application needs to establish a Director of Engineering / Product perspective on the landing page. Two intersecting challenges:

1. **Governance rituals**: Showing how acceptance criteria agreement, test review sessions, and TSR checkpoints build confidence between builders and risk bodies. "Design with the End in Mind" / "Getting to Yes."

2. **New participants in the SDLC**: Agentic coding tools are enabling people who haven't coded before (product managers, business analysts) to write code. Directors of Engineering and Product need to support these new builders in understanding the SDLC — its purpose, its documentation, and how to engage with it to: (a) build the right things, (b) build those things correctly, and (c) not introduce new problems during development.

The five phases should be explicitly labeled as **"The SDLC with AI"** — framing them as the familiar software development lifecycle adapted for AI features.

Additionally: Phase names need updating, Phase 3 (Build) has too much information and needs simplification, and the Governance tab needs to show actual TSR artifacts from the database scoped to specific releases.

---

## Part 1: Phase Name Changes

**"Iterate" → "Iterate & Approve"** and **"Monitor" → "Deploy & Monitor"** in all locations:

| File | Line(s) | Change |
|------|---------|--------|
| `viewer/narrative.py` | 76, 86 | `short_title` in PHASES dict |
| `templates/narrative/landing.html` | 96, 103 | `<h3>` text in phase cards |
| `templates/components/rainbow_arc.html` | 29, 35 | SVG `<text>` labels — use `<tspan>` for two-line labels since text is longer |
| `tests/e2e/test_narrative_flow.py` | 140, 141 | Update assertions to match new names |

**SVG detail**: The rainbow arc SVG labels at positions (415,135) and (510,240) will use `<tspan>` elements for two lines:
```xml
<text x="415" y="128" class="rainbow-arc__title">
  <tspan x="415" dy="0">Iterate</tspan>
  <tspan x="415" dy="14">&amp; Approve</tspan>
</text>
```
Same pattern for "Deploy & Monitor" at (510, 233).

---

## Part 2: Landing Page Restructure

**File**: `templates/narrative/landing.html`

### 2A. Hero Section (lines 8-18)
Update subtitle to address the dual challenge facing engineering and product leadership:
- **AI in the SDLC**: Teams adopting AI need governance guidance — how work gets governed, approved, and tied to business value. Engineers managing agents need repeatable rituals.
- **New builders**: Agentic coding tools are enabling product managers, business analysts, and others who haven't coded before to participate in the SDLC. They need to understand its purpose and documentation to: (1) build the right things, (2) build correctly, and (3) not introduce new problems.

Frame this as "the SDLC is the shared language" — governance provides the structure that both experienced engineers and new builders can follow.

Widen `.landing-hero__subtitle` max-width from 600px → ~750px in `design-system.css`.

### 2B. Three-Part Framework Cards (lines 24-53)
Reframe messaging:
- **Governance**: "AI governance is a people challenge as much as a technical one." Add rituals list (acceptance criteria, test review sessions, TSR tracking).
- **Approvals**: "Design with the End in Mind" and "Getting to Yes" — approvals accelerate, not block. When teams know what "done" looks like from Day 1, the path to go/no-go is predictable.
- **Business Value**: TSR ties test results back to requirements so stakeholders always know where things stand.

New CSS: `.cycle-card__rituals` (teal bullet dots, left-aligned list within centered card).

### 2C. Guiding Principle Quote (lines 55-62)
Replace with rituals-focused version emphasizing governance as accelerator. Same CSS class.

### 2D. TSR Visual Mock Preview (NEW — insert between guiding-principle and rainbow-arc)
Static mock of a completed TSR:
- Header: TSR ID + "GO" decision badge
- Requirements checklist (4 items, green checks)
- Test results bars (Unit 100%, Integration 100%, Security 100%, AI Evals 95%)
- Approval line (name, timestamp)
- Progress callout: "70% complete" bar with framing text

New CSS: `tsr-preview` block (~20 child classes), dark card aesthetic, responsive at 640px.

### 2E. Builder Bridge + SDLC Framing (NEW — between TSR preview and rainbow-arc)
Transition paragraph establishing the SDLC context: The organizational system above establishes the rituals and expectations. The SDLC is the shared language that both experienced engineers and new builders (PMs, BAs using agentic tools) follow. The five phases below show this familiar lifecycle adapted for AI features.

New CSS: `.builder-bridge` (centered text, max-width 800px).

### 2F. Rename "Five Phases of AI Development" → "The SDLC with AI"
**File**: `templates/narrative/landing.html` (line 71)

Change `<h2>` from "Five Phases of AI Development" to "The SDLC with AI" (or "The Software Development Lifecycle with AI"). This explicitly labels the phase flow as the SDLC.

### 2G. Update Phase Card Descriptions (lines 93-107)
Update descriptions for renamed phases:
- Phase 4: "Iterate on AI behavior, discover failure modes, and build confidence for approval."
- Phase 5: "Deploy to production, monitor real usage, and feed learnings back into discovery."

### 2H. Landing Markdown
**File**: `data/narrative/landing.md` — replace with content covering:
- The rituals (Discovery Ritual, Test Review Ritual, TSR Checkpoint)
- The new-builder narrative: agentic tools are changing who participates in the SDLC; the structured approach described here helps everyone — from seasoned engineers to PMs writing their first code — know what "done" looks like and how to get there.

---

## Part 3: Phase 3 (Build) Redesign — Cards Only, No Code

**Goal**: Simplify to establish a common language of test types. One concise description per type with builder/business badges. Remove all code viewing.

### 3A. Simplify Route
**File**: `viewer/narrative.py` (phase_3 function, lines 200-257)

Remove all code-viewing logic (test_type param, show_code param, get_test_code calls, test selection, syntax highlighting). The route only needs:
- `intro_content` from markdown
- `all_type_explanations` dict for card descriptions
- `business_facing_types = {'acceptance', 'ai_acceptance', 'evals'}` (new)
- Pass `test_types=TEST_TYPES` for the loop

Remove: `show_code`, `tests`, `selected_test`, `test_code`, `test_filename`, `app_code`, `app_filename`, `ai_acceptance_tests`, `explanation` from the template context.

### 3B. Rewrite Explanation Markdown Files
**Files**: `data/explanations/{unit,integration,e2e,acceptance,security,performance,steelthread,ai_evals,ai_acceptance}.md`

Each file gets simplified to ~3-5 sentences establishing:
1. What this test type validates (one sentence)
2. One illustrative example scenario (not code — a sentence describing what a test checks)
3. Why it matters for AI systems specifically

Remove: code blocks, tables, detailed subsections, "When to Use" sections. Keep: "Relationship to AI" section (extracted separately by `get_explanation()`).

### 3C. Redesign Template
**File**: `templates/narrative/phase3_implementation.html`

**Keep**: AI eval educational banner (lines 24-62), phase intro content.

**Add**: Responsibility note callout between banner and cards:
- "Governance teams don't review test implementation details — that's the builder's professional obligation. The exception is acceptance tests: business users who own the risk need to understand and validate the acceptance testing approach."

New CSS: `.test-responsibility-note` (info-blue left border).

**Redesign card grid** (lines 70-140):
- Same grid layout but simpler cards — just title, badge(s), and the shortened explanation content
- **Business-Facing badge** (blue) on: AI Acceptance, AI Evals, Acceptance
- **Builder badge** (gray) on: Unit, Integration, E2E, Security, Performance, Steel Thread
- Keep AI badge on AI Acceptance and AI Evals

**Remove entirely**: Code collapsible section (lines 142-244), sidebar navigation, code canvas, run button. The `show_code` parameter and all code-viewing functionality is removed.

New CSS: `.test-type-card__badge--business` and `.test-type-card__badge--builder`.

---

## Part 4: Governance Tab Overhaul — Inline TSR Cards

**Goal**: Replace hardcoded governance_overview content with actual TSR data from the database, framed with context about release-scoped TSRs.

### 4A. Update Governance Route
**File**: `viewer/narrative.py` (governance function, lines 319-327)

Import and use the TSR repository to fetch sample TSRs. The repository is available via `viewer/governance.py`'s `_repository` global. Add logic to:
1. Import or access the repository from the governance module
2. Query TSRs from the database
3. Pass `tsrs` list and `stats` dict to the template

```python
@narrative_bp.route('/governance')
def governance():
    context = get_phase_context('governance')
    intro_content = load_narrative_content('governance_intro.md')

    # Get TSR data from repository
    from .governance import _repository
    tsrs = []
    stats = None
    if _repository:
        tsrs = _repository.query(limit=10)
        total = _repository.count()
        go = _repository.count(decision='go')
        no_go = _repository.count(decision='no_go')
        stats = {
            'total': total, 'go': go, 'no_go': no_go,
            'go_rate': go / total if total > 0 else 0
        }

    return render_template('narrative/governance_overview.html',
                           intro_content=intro_content,
                           tsrs=tsrs, stats=stats,
                           **context)
```

### 4B. Redesign Governance Template
**File**: `templates/narrative/governance_overview.html`

Replace the current hardcoded content with:

1. **Intro content** from `governance_intro.md` (keep existing pattern)

2. **Release Scoping Callout** (NEW):
   "Each Test Summary Report is scoped to the specific changes in a release — not a re-test of the entire application. This means TSRs are lightweight, focused artifacts that document what changed, what was tested, and whether it's safe to deploy."

3. **TSR Cards Grid** (embed from database):
   Reuse the `.tsr-card` styles from `governance/dashboard.html` — move those styles to `governance.css` or `design-system.css` so they're shared. Each card shows:
   - TSR ID + decision badge (GO/NO-GO/PENDING)
   - Version name (V1 Verbose, V2 No RAG, V3 RAG) from eval iterations
   - Environment, creation date
   - Link to full TSR detail: `url_for('governance.tsr_detail', tsr_id=tsr.id)`

4. **Fallback**: If no TSRs in database, show a message: "No TSRs found. Run `python3 scripts/seed_test_data.py` to create sample data."

5. **Keep**: "Journey Complete" section at the bottom with the key takeaway.

**Remove**: Hardcoded cross-phase summary table, compliance considerations section (these are better shown in the actual TSR detail pages).

### 4C. Update Governance Intro Markdown
**File**: `data/narrative/governance_intro.md`

Update to focus on:
- TSRs as the central governance artifact
- Each TSR is scoped to a specific release
- The governance tab shows the real artifacts that were created through the development process
- Link back to the rituals established on the landing page

### 4D. Share TSR Card Styles
Move the `.tsr-card` styles from inline `<style>` in `governance/dashboard.html` to `static/css/governance.css` (which already exists and is linked by `tsr_detail.html`). Then link `governance.css` from both `governance_overview.html` and `dashboard.html`.

---

## Part 5: Tests

**File**: `tests/e2e/test_narrative_flow.py`

**Update existing**:
- `test_landing_phase_cards_updated` (line 133): change `Iterate` → `Iterate` (still present as substring), add `Approve` check; change `Monitor` → `Deploy` check
- `test_phase3_show_code_param` (line 56): **remove** — show_code no longer exists
- `test_phase3_accepts_test_type_param` (line 51): **remove** — test_type param for code viewing removed

**Add new**:
- `test_landing_tsr_preview`: assert `tsr-preview` class and `Test Summary Report` text
- `test_landing_builder_bridge`: assert `builder-bridge` class
- `test_phase3_business_facing_badge`: assert `Business-Facing` in response
- `test_phase3_responsibility_note`: assert `test-responsibility-note` in response
- `test_governance_shows_tsrs` (or update `test_governance_page_loads`): verify TSR content appears when database has seed data (may need conditional assertion)

---

## Files Modified (Summary)

| File | Change |
|------|--------|
| `viewer/narrative.py` | PHASES short_titles, simplify phase_3 route, add TSR data to governance route |
| `templates/narrative/landing.html` | Hero, framework cards, quote, TSR preview, builder bridge, phase card descriptions |
| `templates/components/rainbow_arc.html` | SVG multi-line labels for Phase 4 & 5 |
| `templates/narrative/phase3_implementation.html` | Redesign: cards-only with badges, remove code section |
| `templates/narrative/governance_overview.html` | Replace hardcoded content with inline TSR cards + scoping context |
| `static/css/design-system.css` | ~150 lines: tsr-preview, cycle-card__rituals, builder-bridge, test-responsibility-note, badge modifiers |
| `static/css/governance.css` | Move tsr-card styles from dashboard inline to shared CSS |
| `templates/governance/dashboard.html` | Remove inline tsr-card styles, link to governance.css |
| `data/narrative/landing.md` | Rituals-focused content |
| `data/narrative/governance_intro.md` | TSR-focused, release-scoped framing |
| `data/explanations/*.md` (9 files) | Simplify to 3-5 sentence descriptions, keep Relationship to AI section |
| `tests/e2e/test_narrative_flow.py` | Update phase name assertions, remove code-viewing tests, add new tests |
| `.claude/affordances.md` | New affordance entries |

---

## Implementation Order

1. Phase name changes (PHASES dict, landing cards, rainbow arc SVG, tests) — smallest blast radius
2. CSS additions (additive, no breakage)
3. Landing page template + markdown
4. Explanation markdown simplification (9 files)
5. Phase 3 route simplification + template redesign
6. Governance route update + template overhaul + shared CSS
7. Tests (update + add)
8. Lint (`black` then `flake8`)
9. Affordances update

## Verification

1. `source .venv/bin/activate && python3 -m pytest tests/e2e/test_narrative_flow.py -v` — all tests pass
2. `python3 -m pytest tests/unit/ -v` — no regressions
3. Seed TSR data: `cd ai-testing-resource && python3 scripts/seed_test_data.py`
4. Visual check: `python3 app.py` then browse:
   - `localhost:5000/` — hero, framework cards with rituals, TSR mock, builder bridge, renamed phase cards
   - `localhost:5000/phase/3` — simplified cards with badges, no code section
   - `localhost:5000/governance` — inline TSR cards from database, scoping context
5. Rainbow arc: verify two-line phase labels render correctly
6. Responsive: check at <640px width
