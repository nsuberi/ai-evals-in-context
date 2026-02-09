# Phase 4 Improvements: Dynamic Trace Switching, LangSmith-Style Visualization & Navigation Cleanup

## Context

Phase 4 ("Iterate and Approve") currently demonstrates the evolution of an AI chatbot through three versions (v1 → v2 → v3), showing how testing identifies failure modes and drives iteration. However, the current implementation has several limitations:

1. **Page Reloads**: Switching between traces causes full page reloads, creating a jarring user experience
2. **Limited RAG Visibility**: Traces don't show the complete RAG pipeline (ChromaDB retrieval, context building, prompt construction)
3. **Text-Heavy Architecture**: The "Architecture Context" dropdown uses text descriptions rather than visual trace representations
4. **Duplicate Navigation**: The "Tools View" button provides access to legacy standalone views (`/viewer/tests`, `/viewer/traces`, `/viewer/timeline`) that duplicate content already embedded in the narrative phases

This plan addresses these issues by implementing dynamic trace switching, complete RAG pipeline capture, LangSmith-style span visualization, and removing legacy viewer routes. Additionally, it configures the production deployment to automatically seed traces and sample TSRs on startup.

**Problem Being Solved:**
- Users can't see "under the hood" of how RAG works - they only see final responses
- Switching between examples disrupts the learning flow with page reloads
- Architecture explanations are verbose text rather than self-evident from the trace structure

**Intended Outcome:**
- Seamless, instant switching between trace examples without page reloads
- Complete visibility into RAG pipeline: query → embedding → retrieval → context → prompt → LLM
- Visual span tree (like LangSmith) that makes architecture obvious from the nested structure
- Production deployment automatically includes all demo data (traces, TSRs, knowledge base)
- Clean navigation without legacy duplicate views

---

## Implementation Plan

### 0. Remove Legacy Viewer Routes (Cleanup)

**Problem:** The "Tools View" button in the navigation provides access to legacy standalone views that duplicate content already embedded in the narrative:
- `/viewer/tests` → Duplicates Phase 3 test navigation
- `/viewer/traces` → Duplicates Phase 4 trace inspection
- `/viewer/timeline` → Duplicates Phase 4 iteration comparison

**Solution:** Remove the navigation button, route handlers, and templates. Keep helper functions that are used by narrative phases.

#### 0a. Remove "Tools View" Button

**File**: `ai-testing-resource/templates/components/phase_nav.html`

**Delete lines 33-38:**
```html
<!-- REMOVE THIS SECTION -->
<!-- Legacy Navigation Link -->
<div class="phase-nav__legacy">
  <a href="{{ url_for('viewer.test_navigator', test_type='unit') }}" class="phase-nav__legacy-link">
    Tools View
  </a>
</div>
```

#### 0b. Remove Viewer Route Handlers

**File**: `ai-testing-resource/viewer/routes.py`

**Delete these routes:**
1. `test_navigator()` (lines 15-62) - DELETE
2. `run_test()` (lines 65-99) - DELETE (was used by test_navigator)
3. `trace_inspector()` (lines 102-126) - DELETE
4. `iteration_timeline()` (lines 129-138) - DELETE

**Keep the imports** - The helper functions are still used by narrative.py:
- `get_tests_by_type`, `get_test_code`, `get_explanation`, `TEST_TYPES` → Used by Phase 3
- `get_traces_by_version`, `get_trace_detail`, `render_annotated_response` → Used by Phase 4
- `get_iteration_summary`, `get_comparison_data` → Used by Phase 4

**Result**: `viewer/routes.py` will be an empty file (just Blueprint definition and imports) or can be deleted entirely if no other routes exist.

#### 0c. Delete Viewer Templates

**Delete these files:**
1. `ai-testing-resource/templates/test_navigator.html`
2. `ai-testing-resource/templates/trace_inspector.html`
3. `ai-testing-resource/templates/iteration_timeline.html`

These templates were ONLY used by the viewer routes being removed. The narrative phases have their own templates in `templates/narrative/`.

#### 0d. Remove Legacy CSS Styles

**File**: `ai-testing-resource/static/css/design-system.css`

**Search and delete** any CSS rules for:
- `.phase-nav__legacy`
- `.phase-nav__legacy-link`

#### 0e. Update Tests

**Files to update:**

1. **`ai-testing-resource/tests/e2e/test_narrative_flow.py`** (lines 199-220)
   - DELETE tests: `test_viewer_tests_route`, `test_viewer_tests_with_type`, `test_viewer_traces_route`, `test_viewer_traces_with_version`, `test_viewer_timeline_route`
   - These tests verify legacy routes that we're removing

2. **`ai-testing-resource/tests/playwright/test_browser.py`** (lines 60-82)
   - DELETE tests: test_test_navigator, test_trace_inspector, test_iteration_timeline
   - These test the viewer pages we're removing

3. **`ai-testing-resource/tests/steelthread/test_narrative_steel_thread.py`** (lines 114-116)
   - REMOVE these URLs from the `critical_endpoints` list:
     - `/viewer/tests`
     - `/viewer/traces`
     - `/viewer/timeline`

4. **`ai-testing-resource/tests/playwright/test_steel_thread.py` and `tests/steelthread/test_steel_thread.py`**
   - DELETE `test_full_journey_portfolio_to_viewer_tests` (tests navigation to /viewer/tests which we're removing)

#### 0f. Update Documentation

**Files to update:**

1. **`ai-testing-resource/README.md`** (lines 138-140)
   - DELETE the "Legacy Routes" section showing `/viewer/*` URLs

2. **`.claude/affordances.md`**
   - DELETE affordances for:
     - Test Navigator place
     - Trace Inspector place
     - Iteration Timeline place
   - DELETE wiring entries that reference `/viewer/tests`, `/viewer/traces`, `/viewer/timeline`

3. **`ai-testing-resource/templates/base.html`** (lines 24-28)
   - If there's a nav menu with links to viewer routes, remove those links

#### 0g. Update JavaScript References

**File**: `ai-testing-resource/static/js/viewer.js`

**Check for references** to `/viewer/*` routes:
- Line 68: `url.pathname = appUrl('/viewer/traces/${version}');` - DELETE or update to narrative route
- Line 74: `window.location.href = appUrl('/viewer/tests/${testType}');` - DELETE or update

**These functions may need to be updated or removed** depending on how they're used in the narrative.

---

### 1. Span Data Structure (New Trace Format)

**File**: `ai-testing-resource/data/traces/v{1,2,3}_traces.json`

Add an optional `spans` field to v3 traces (v1 and v2 remain unchanged since they don't use RAG):

```json
{
  "id": "v3-trace-001",
  "version": "v3",
  "question": "What is your return policy?",
  "response": "We offer a 30-day return window...",
  "latency_ms": 2341,
  "tokens": {"prompt": 450, "completion": 85},
  "sources": [{"id": "return_policy", "title": "Return Policy"}],
  "annotations": [...],
  "spans": [
    {
      "span_id": "span-1",
      "name": "Query Embedding",
      "span_type": "embedding",
      "start_time": 0,
      "duration_ms": 45,
      "input": {"text": "What is your return policy?"},
      "output": {"dimensions": 384, "preview": "[0.123, -0.456, ...]"},
      "metadata": {"model": "all-MiniLM-L6-v2"}
    },
    {
      "span_id": "span-2",
      "name": "ChromaDB Retrieval",
      "span_type": "retrieval",
      "start_time": 45,
      "duration_ms": 120,
      "input": {"embedding_dim": 384, "n_results": 3},
      "output": {
        "documents": [
          {
            "id": "return_policy",
            "title": "Return Policy",
            "distance": 0.234,
            "content_preview": "Acme Widgets Return Policy..."
          }
        ]
      },
      "metadata": {"collection": "acme_knowledge_base"}
    },
    {
      "span_id": "span-3",
      "name": "Context Building",
      "span_type": "context",
      "start_time": 165,
      "duration_ms": 12,
      "input": {"doc_count": 2},
      "output": {"context_length": 1245, "preview": "[Return Policy]\n..."},
      "metadata": {"separator": "\\n\\n---\\n\\n"}
    },
    {
      "span_id": "span-4",
      "name": "Prompt Construction",
      "span_type": "prompt",
      "start_time": 177,
      "duration_ms": 8,
      "input": {"template": "V3_SYSTEM_PROMPT"},
      "output": {"prompt_length": 1567, "preview": "You are a helpful..."},
      "metadata": {"template_version": "v3"}
    },
    {
      "span_id": "span-5",
      "name": "Claude API Call",
      "span_type": "llm",
      "start_time": 185,
      "duration_ms": 2156,
      "input": {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 512,
        "message_preview": "What is your return policy?"
      },
      "output": {
        "response_preview": "We offer a 30-day...",
        "usage": {"input_tokens": 450, "output_tokens": 85},
        "stop_reason": "end_turn"
      },
      "metadata": {"api_version": "2023-06-01"}
    }
  ]
}
```

**Backward Compatibility:**
- V1 and V2 traces: No changes (no `spans` field, no RAG pipeline)
- V3 traces: Add `spans` array
- Frontend checks for presence of `spans` before rendering span tree

---

### 2. Trace Generation Script Updates

**File**: `ai-testing-resource/scripts/generate_traces.py`

**Changes:**
- Add `generate_v3_span_trace()` function to create span structures
- Simulate RAG pipeline timing for each v3 trace
- Keep existing v1/v2 trace generation unchanged

**Simulated Spans for V3:**
1. **Query Embedding** (~40-60ms): Mock sentence-transformer timing
2. **ChromaDB Retrieval** (~100-150ms): Use actual KB docs with simulated distances
3. **Context Building** (~5-15ms): String concatenation timing
4. **Prompt Construction** (~5-10ms): Template filling timing
5. **Claude API Call** (~1800-2500ms): Simulated API latency

**Script Execution:**
```bash
cd ai-testing-resource/
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)  # Load ANTHROPIC_API_KEY
python3 scripts/generate_traces.py  # Regenerates all trace files
```

**Output:**
- `data/traces/v1_traces.json` (unchanged - 20 traces)
- `data/traces/v2_traces.json` (unchanged - 20 traces)
- `data/traces/v3_traces.json` (updated with `spans` - 20 traces)

---

### 3. API Endpoint for Dynamic Trace Fetching

**File**: `ai-testing-resource/viewer/narrative.py`

**New Route:**
```python
@narrative_bp.route("/api/phase4/trace/<version>/<trace_id>")
def api_get_trace(version: str, trace_id: str):
    """API endpoint for AJAX trace fetching (no page reload)."""
    trace_detail = get_trace_detail(trace_id)
    if not trace_detail:
        return jsonify({"error": "Trace not found"}), 404

    # Render annotated response server-side
    annotated_response = render_annotated_response(
        trace_detail.get("response", ""),
        trace_detail.get("annotations", [])
    )

    return jsonify({
        "trace_id": trace_id,
        "version": version,
        "trace_detail": trace_detail,
        "annotated_response": annotated_response,
        "has_spans": "spans" in trace_detail and len(trace_detail.get("spans", [])) > 0
    })
```

**Response Format:**
```json
{
  "trace_id": "v3-trace-001",
  "version": "v3",
  "trace_detail": { /* full trace object with spans */ },
  "annotated_response": "<div class='ann ann--success'>...</div>",
  "has_spans": true
}
```

---

### 4. Frontend JavaScript for Dynamic Switching

**File**: `ai-testing-resource/static/js/viewer.js`

**New Functions:**

```javascript
// Switch to a different trace without page reload
async function switchTrace(version, traceId) {
  const mainContent = document.querySelector('.content-primary');
  const sidebarItems = document.querySelectorAll('.sidebar__item');

  // Update sidebar active state (optimistic UI)
  sidebarItems.forEach(item => {
    if (item.dataset.traceId === traceId) {
      item.classList.add('sidebar__item--active');
    } else {
      item.classList.remove('sidebar__item--active');
    }
  });

  // Show loading state
  mainContent.innerHTML = '<div class="loading-spinner">Loading trace...</div>';

  try {
    const response = await fetch(appUrl(`/api/phase4/trace/${version}/${traceId}`));
    const data = await response.json();

    if (!response.ok) throw new Error(data.error || 'Failed to load trace');

    // Render trace detail
    renderTraceDetail(data);

    // Update URL without reload (for back button support)
    const url = new URL(window.location);
    url.searchParams.set('trace', traceId);
    window.history.pushState({version, traceId}, '', url.toString());

  } catch (error) {
    mainContent.innerHTML = `<div class="error-message">Error: ${escapeHtml(error.message)}</div>`;
  }
}

// Render complete trace detail (response + spans + metadata)
function renderTraceDetail(data) {
  const mainContent = document.querySelector('.content-primary');

  const html = `
    <!-- Question -->
    <div class="explanation">
      <h3 class="explanation__title">Question</h3>
      <div class="explanation__content">${escapeHtml(data.trace_detail.question)}</div>
    </div>

    <!-- Annotated Response -->
    <div class="code-canvas">
      <div class="code-canvas__header">
        <span class="code-canvas__filename">Response</span>
        <span class="code-canvas__badge" style="background: var(--color-${getVersionColor(data.version)});">
          ${data.version.toUpperCase()}
        </span>
      </div>
      <div class="code-canvas__code" style="font-family: var(--font-prose); white-space: pre-wrap;">
        ${data.annotated_response}
      </div>
      ${renderAnnotationFootnotes(data.trace_detail.annotations)}
    </div>

    <!-- RAG Pipeline Span Tree (if spans exist) -->
    ${data.has_spans ? renderSpanTree(data.trace_detail.spans, data.trace_detail.latency_ms) : ''}

    <!-- Secondary Content -->
    <div class="content-secondary">
      ${renderPromptCollapsible(data.trace_detail.prompt)}
      ${renderMetadata(data.trace_detail)}
    </div>
  `;

  mainContent.innerHTML = html;
}

// Render LangSmith-style span tree visualization
function renderSpanTree(spans, totalLatency) {
  if (!spans || spans.length === 0) return '';

  const sortedSpans = [...spans].sort((a, b) => a.start_time - b.start_time);

  const spanHtml = sortedSpans.map(span => {
    const percentDuration = (span.duration_ms / totalLatency) * 100;
    const spanColor = getSpanColor(span.span_type);

    return `
      <div class="span-item span-item--${span.span_type}" data-span-id="${span.span_id}">
        <div class="span-item__header" onclick="toggleSpan(this.parentElement)">
          <span class="span-item__icon">▶</span>
          <span class="span-item__name">${escapeHtml(span.name)}</span>
          <span class="span-item__duration">${span.duration_ms}ms</span>
          <div class="span-item__bar" style="width: ${percentDuration}%; background: ${spanColor};"></div>
        </div>
        <div class="span-item__body">
          <div class="span-item__section">
            <div class="span-item__label">Input</div>
            <pre class="span-item__code">${escapeHtml(JSON.stringify(span.input, null, 2))}</pre>
          </div>
          <div class="span-item__section">
            <div class="span-item__label">Output</div>
            <pre class="span-item__code">${escapeHtml(JSON.stringify(span.output, null, 2))}</pre>
          </div>
          ${span.metadata ? `
            <div class="span-item__section">
              <div class="span-item__label">Metadata</div>
              <pre class="span-item__code">${escapeHtml(JSON.stringify(span.metadata, null, 2))}</pre>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }).join('');

  return `
    <div class="span-tree">
      <div class="span-tree__header">
        <h3>RAG Pipeline Trace</h3>
        <span class="span-tree__total">Total: ${totalLatency}ms</span>
      </div>
      <div class="span-tree__timeline">${spanHtml}</div>
    </div>
  `;
}

// Color mapping for span types
function getSpanColor(spanType) {
  const colors = {
    embedding: '#4A9EFF',    // Blue
    retrieval: '#9B59B6',    // Purple
    context: '#F39C12',      // Orange
    prompt: '#E74C3C',       // Red
    llm: '#2ECC71'           // Green
  };
  return colors[spanType] || '#95a5a6';
}

// Toggle span expansion
function toggleSpan(spanElement) {
  spanElement.classList.toggle('span-item--expanded');
}

// Helper functions (renderAnnotationFootnotes, renderPromptCollapsible, renderMetadata)
// ... (implementation details)
```

**Browser History Support:**
```javascript
// Handle back/forward button
window.addEventListener('popstate', (event) => {
  if (event.state && event.state.traceId) {
    switchTrace(event.state.version, event.state.traceId);
  }
});
```

---

### 5. Template Updates for Dynamic Switching

**File**: `ai-testing-resource/templates/narrative/phase4_evaluation.html`

**Changes:**

1. **Update trace sidebar links** (from href navigation to onclick):
```html
<a href="javascript:void(0)"
   class="sidebar__item {% if trace.id == selected_trace %}sidebar__item--active{% endif %}"
   data-trace-id="{{ trace.id }}"
   onclick="switchTrace('{{ current_version }}', '{{ trace.id }}')">
  {{ trace.question }}
  {% if trace.has_annotations %}
  <span style="color: var(--color-warning);">*</span>
  {% endif %}
</a>
```

2. **Remove "Architecture Context" section** (replaced by dynamic span tree)

3. **Add container for dynamic content** (main content area already exists, no change needed)

---

### 6. CSS Styling for Span Tree Visualization

**File**: `ai-testing-resource/static/css/design-system.css`

**New Styles:**

```css
/* Span Tree Container */
.span-tree {
  margin: var(--space-lg) 0;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.span-tree__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) var(--space-lg);
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.span-tree__header h3 {
  margin: 0;
  font-size: 1rem;
  color: var(--color-chrome-text-bright);
}

.span-tree__total {
  font-size: 0.875rem;
  color: var(--color-chrome-text);
  font-weight: 500;
}

/* Span Items */
.span-item {
  margin-bottom: var(--space-sm);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  overflow: hidden;
}

.span-item__header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  position: relative;
}

.span-item__header:hover {
  background: rgba(255, 255, 255, 0.05);
}

.span-item__icon {
  font-size: 0.625rem;
  color: var(--color-chrome-text);
  transition: transform 0.2s;
}

.span-item--expanded .span-item__icon {
  transform: rotate(90deg);
}

.span-item__name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-chrome-text-bright);
  flex: 1;
}

.span-item__duration {
  font-size: 0.75rem;
  color: var(--color-chrome-text);
  font-family: var(--font-code);
  margin-right: var(--space-md);
}

.span-item__bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  transition: width 0.3s;
}

.span-item__body {
  display: none;
  padding: var(--space-md);
  background: rgba(0, 0, 0, 0.3);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.span-item--expanded .span-item__body {
  display: block;
}

.span-item__section {
  margin-bottom: var(--space-md);
}

.span-item__label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--color-chrome-text);
  margin-bottom: var(--space-xs);
  font-weight: 600;
}

.span-item__code {
  margin: 0;
  padding: var(--space-sm);
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  font-family: var(--font-code);
  font-size: 0.75rem;
  color: var(--color-chrome-text-bright);
  overflow-x: auto;
  white-space: pre-wrap;
}

/* Span type color variants */
.span-item--embedding .span-item__name { color: #4A9EFF; }
.span-item--retrieval .span-item__name { color: #9B59B6; }
.span-item--context .span-item__name { color: #F39C12; }
.span-item--prompt .span-item__name { color: #E74C3C; }
.span-item--llm .span-item__name { color: #2ECC71; }

/* Loading State */
.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: var(--color-chrome-text);
  font-size: 1rem;
}

.loading-spinner::before {
  content: '⏳';
  font-size: 2rem;
  margin-right: var(--space-md);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

### 7. Production Deployment Seeding

**Problem:** Production deployment needs to include demo data:
- Traces (static JSON files)
- ChromaDB knowledge base (markdown docs → vector embeddings)
- TSR database (sample test summary reports)

**Solution:** Multi-stage approach

#### 7a. Update Dockerfile for Build-Time Trace Generation

**File**: `ai-testing-resource/Dockerfile`

**Changes:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create directories for data persistence
RUN mkdir -p /app/chroma_db /app/data/knowledge_base /app/data/traces /app/results

# Generate trace files at build time (no API key needed - uses simulated data)
RUN python3 scripts/generate_traces.py

# Expose Flask port
EXPOSE 5000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/tsr/stats || exit 1

# Use entrypoint script for runtime initialization
COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
```

#### 7b. Create Entrypoint Script for Runtime Seeding

**File**: `ai-testing-resource/scripts/entrypoint.sh` (new file)

```bash
#!/bin/bash
set -e

echo "=== AI Testing Resource - Starting ==="

# Step 1: Initialize TSR database tables
echo "Initializing TSR database..."
python3 scripts/init_database.py || {
  echo "Warning: Database initialization failed (may already exist)"
}

# Step 2: Seed sample TSR data (idempotent - only seeds if empty)
echo "Seeding sample TSR data..."
python3 scripts/seed_test_data.py || {
  echo "Warning: TSR seeding failed (may already exist)"
}

# Step 3: Start the Flask application
# Note: run.py already calls initialize_knowledge_base() which seeds ChromaDB
echo "Starting Flask application..."
exec python3 run.py
```

**What This Does:**
1. **init_database.py**: Creates TSR tables in RDS PostgreSQL (idempotent - skips if exists)
2. **seed_test_data.py**: Creates 3 sample TSRs (V1, V2, V3) (idempotent - skips if not empty)
3. **run.py**: Starts Flask, which calls `initialize_knowledge_base()` to seed ChromaDB

**Idempotency:** All scripts check if data exists before seeding, so re-deployments won't duplicate data.

#### 7c. Update GitHub Actions CI to Use Entrypoint

**File**: `.github/workflows/ai-app-ci.yml`

No changes needed - Docker Compose already uses the Dockerfile's ENTRYPOINT.

#### 7d. Update Terraform to Ensure Database is Ready

**File**: `terraform/modules/ecs/main.tf`

**Check Current State:**
- Task definition already includes `TSR_DATABASE_URL` environment variable
- Container depends on RDS being available

**Potential Addition:** Increase health check grace period to allow seeding time:
```hcl
health_check_grace_period_seconds = 120  # Increase from default 60s to allow DB seeding
```

---

### 8. Testing Strategy

#### Unit Tests
**File**: `ai-testing-resource/tests/unit/test_narrative.py` (new tests)

```python
def test_api_get_trace_endpoint(client):
    """Test API endpoint returns trace JSON without page reload"""
    response = client.get('/api/phase4/trace/v3/v3-trace-001')
    assert response.status_code == 200
    data = response.get_json()
    assert 'trace_detail' in data
    assert 'annotated_response' in data
    assert data['has_spans'] == True

def test_api_get_trace_not_found(client):
    """Test API endpoint returns 404 for missing trace"""
    response = client.get('/api/phase4/trace/v3/nonexistent')
    assert response.status_code == 404
```

#### Integration Tests
**File**: `ai-testing-resource/tests/integration/test_trace_generation.py` (new)

```python
def test_generated_traces_have_valid_spans():
    """Test that generated v3 traces include valid span structures"""
    traces = get_traces_by_version('v3')
    for trace_id in [t['id'] for t in traces]:
        trace = get_trace_detail(trace_id)
        assert 'spans' in trace
        assert len(trace['spans']) == 5  # embedding, retrieval, context, prompt, llm

        # Verify span timing is cumulative
        for i, span in enumerate(trace['spans']):
            if i > 0:
                prev_end = trace['spans'][i-1]['start_time'] + trace['spans'][i-1]['duration_ms']
                assert span['start_time'] >= prev_end
```

#### E2E Tests
**File**: `ai-testing-resource/tests/e2e/test_narrative_flow.py` (update existing)

```python
def test_phase4_trace_switching_links_exist(client):
    """Test that Phase 4 trace sidebar has onclick handlers"""
    response = client.get('/phase/4?version=v3')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    # Check for onclick handlers (not href navigation)
    assert 'onclick="switchTrace(' in html
    assert 'data-trace-id=' in html
```

#### Playwright Browser Tests
**File**: `ai-testing-resource/tests/playwright/test_phase4_dynamic.py` (new)

```python
def test_trace_switching_without_reload(page, base_url):
    """Test clicking trace in sidebar updates content without page reload"""
    page.goto(f"{base_url}/phase/4?version=v3")

    # Click first trace
    page.click('.sidebar__item[data-trace-id="v3-trace-001"]')
    page.wait_for_selector('.code-canvas__code', state='visible')
    first_response = page.inner_text('.code-canvas__code')

    # Click second trace
    page.click('.sidebar__item[data-trace-id="v3-trace-002"]')
    page.wait_for_selector('.loading-spinner', state='hidden')
    second_response = page.inner_text('.code-canvas__code')

    # Verify content changed
    assert first_response != second_response

    # Verify URL updated (without reload)
    assert 'trace=v3-trace-002' in page.url

def test_span_tree_renders_for_v3(page, base_url):
    """Test span tree visualization appears for v3 traces"""
    page.goto(f"{base_url}/phase/4?version=v3")

    # Wait for page load
    page.wait_for_selector('.span-tree', state='visible')

    # Verify span tree structure
    spans = page.query_selector_all('.span-item')
    assert len(spans) == 5  # embedding, retrieval, context, prompt, llm

    # Test span expansion
    first_span = spans[0]
    first_span.click()
    assert 'span-item--expanded' in first_span.get_attribute('class')

    # Verify input/output sections visible
    assert page.is_visible('.span-item__section .span-item__label:has-text("Input")')
    assert page.is_visible('.span-item__section .span-item__label:has-text("Output")')
```

---

## Critical Files to Modify

### Additions/Modifications
| File | Purpose | LOC Change |
|------|---------|------------|
| `ai-testing-resource/scripts/generate_traces.py` | Add v3 span generation | +200 |
| `ai-testing-resource/viewer/narrative.py` | Add API endpoint | +50 |
| `ai-testing-resource/static/js/viewer.js` | Dynamic switching + span rendering | +150 |
| `ai-testing-resource/static/css/design-system.css` | Span tree styles | +120 |
| `ai-testing-resource/templates/narrative/phase4_evaluation.html` | Update sidebar links | ~30 |
| `ai-testing-resource/Dockerfile` | Add trace generation + entrypoint | +10 |
| `ai-testing-resource/scripts/entrypoint.sh` | Runtime seeding script (new) | +30 |
| `.claude/affordances.md` | Document new affordances | +10 |

### Deletions/Removals
| File | Purpose | LOC Removed |
|------|---------|-------------|
| `templates/components/phase_nav.html` | Remove "Tools View" button | -6 |
| `viewer/routes.py` | Remove viewer route handlers | -138 |
| `templates/test_navigator.html` | Delete legacy template | DELETE FILE |
| `templates/trace_inspector.html` | Delete legacy template | DELETE FILE |
| `templates/iteration_timeline.html` | Delete legacy template | DELETE FILE |
| `static/css/design-system.css` | Remove legacy nav CSS | -10 |
| `tests/e2e/test_narrative_flow.py` | Remove legacy route tests | -25 |
| `tests/playwright/test_browser.py` | Remove viewer page tests | -30 |
| `tests/steelthread/*.py` | Remove viewer route refs | -20 |
| `README.md` | Remove legacy route docs | -5 |
| `.claude/affordances.md` | Remove viewer affordances | -15 |

**Total Impact:** ~600 new lines, ~250 removed lines, 3 deleted files

---

## Implementation Sequence

### Day 1: Cleanup Legacy Viewer Routes
1. Remove "Tools View" button from `templates/components/phase_nav.html`
2. Delete viewer route handlers from `viewer/routes.py`
3. Delete legacy templates: `test_navigator.html`, `trace_inspector.html`, `iteration_timeline.html`
4. Remove legacy CSS styles from `design-system.css`
5. Update JavaScript in `viewer.js` (remove viewer route references)
6. Update tests to remove legacy route tests
7. Update documentation (README.md, affordances.md)
8. Test that app still runs (python3 run.py)
9. Run unit + e2e tests to catch any breakage

### Day 2: Trace Generation & API
10. Update `scripts/generate_traces.py` to add v3 span generation
11. Regenerate v3 trace files locally
12. Add API endpoint to `viewer/narrative.py`
13. Test API endpoint returns correct JSON
14. Run unit tests

### Day 3: Frontend Dynamic Switching
15. Add span tree CSS to `design-system.css`
16. Add JavaScript functions to `viewer.js` (switchTrace, renderTraceDetail, renderSpanTree)
17. Update `phase4_evaluation.html` template to use onclick handlers
18. Test dynamic switching in browser locally
19. Test URL history management (back button)

### Day 4: Deployment Seeding
20. Create `scripts/entrypoint.sh`
21. Update `Dockerfile` to use entrypoint
22. Test Docker build locally (`docker build -t test:local .`)
23. Test Docker container startup with seeding (`docker run --env-file .env -p 5000:5000 test:local`)
24. Verify traces, ChromaDB, and TSRs are seeded in container

### Day 5: Testing & Polish
25. Add E2E tests for API endpoint
26. Add Playwright tests for dynamic switching
27. Run full test suite (unit + integration + e2e + playwright)
28. Lint all changed files (`black`, `flake8`)
29. Update affordances documentation (final pass)
30. Commit changes

### Day 6: Deployment
31. Deploy to AWS ECS (`./scripts/deploy.sh`)
32. Verify deployment health (`./scripts/verify-deployment.sh`)
33. Check CloudWatch logs for seeding success
34. Test production site: https://portfolio.cookinupideas.com/ai-evals/phase/4
35. Verify traces switch dynamically in production
36. Verify span tree renders for v3 traces
37. Verify "Tools View" button is gone from navigation

---

## Verification Plan

**Local Verification:**
```bash
# 0. Cleanup verification (FIRST)
cd ai-testing-resource/
source .venv/bin/activate

python3 run.py
# - Navigate to http://localhost:5000/
# - Verify "Tools View" button is GONE from navigation
# - Try accessing http://localhost:5000/viewer/tests (should 404)
# - Try accessing http://localhost:5000/viewer/traces (should 404)
# - Navigate to Phase 3 and Phase 4 (should still work normally)

# 1. Generate traces
export $(grep -v '^#' .env | xargs)
python3 scripts/generate_traces.py

# 2. Run app locally
python3 run.py

# 3. Test dynamic trace switching
# - Navigate to http://localhost:5000/phase/4?version=v3
# - Click different traces in sidebar (should NOT reload page)
# - Verify URL updates but page doesn't flash
# - Click on span items to expand (should show input/output)
# - Verify back button navigates between traces

# 4. Run tests
python3 -m pytest tests/unit/ tests/e2e/ -v
docker compose up -d --build
python3 -m pytest tests/playwright/test_phase4_dynamic.py --base-url http://localhost:5001 -v
docker compose down
```

**Production Verification:**
```bash
# 1. Deploy
cd ai-testing-resource/
./scripts/deploy.sh

# 2. Check deployment status
aws ecs describe-services \
  --cluster ai-testing-resource-prod \
  --services ai-testing-resource-prod \
  --query 'services[0].{desiredCount:desiredCount,runningCount:runningCount,deployments:deployments}' \
  --output table

# 3. Check logs for seeding
aws logs tail /ecs/ai-testing-resource-prod --since 10m --follow
# Look for:
# - "Generating traces..."
# - "Initializing TSR database..."
# - "Seeding sample TSR data..."
# - "Knowledge base initialized"

# 4. Verify in browser
# - Visit https://portfolio.cookinupideas.com/ai-evals/phase/4
# - Test dynamic trace switching
# - Verify span tree for v3 traces
# - Check network tab: should see fetch to /api/phase4/trace/v3/... (not full page reload)
```

---

## Future Enhancements

**Post-MVP:**
1. **Live Instrumentation**: Capture real spans during actual RAG pipeline execution (not simulated)
2. **Nested Spans**: Support parent-child relationships (e.g., retrieval as child of RAG span)
3. **Flamegraph View**: Alternative visualization showing call stack
4. **Span Comparison**: Side-by-side comparison between v1/v2/v3
5. **Export**: Download span tree as JSON or screenshot
6. **Filtering**: Show/hide span types, filter by duration
7. **Search**: Full-text search within span inputs/outputs
8. **Real-time Traces**: WebSocket stream of live traces as they're generated

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Large trace files** | Slow page load, high memory | Truncate large outputs in span JSON (first 200 chars + "...") |
| **API endpoint latency** | Slow switching | Cache trace JSON in-memory, use gzip compression |
| **Browser history complexity** | Back button breaks | Implement popstate handler, test thoroughly |
| **Seeding fails in production** | No demo data | Make seeding idempotent with graceful degradation, add logs |
| **Database connection timeout** | Container crash on startup | Increase health check grace period, add retry logic to init script |

---

## Success Criteria

✅ **Navigation Cleanup:** "Tools View" button removed, legacy `/viewer/*` routes return 404
✅ **Dynamic Switching:** Clicking trace sidebar item updates content without page reload
✅ **Span Visualization:** V3 traces show hierarchical span tree with timing bars
✅ **Complete RAG Visibility:** Users can see query → embedding → retrieval → context → prompt → LLM flow
✅ **Production Seeding:** Deployed site includes all traces, TSRs, and knowledge base automatically
✅ **Performance:** Trace switching completes in <500ms
✅ **Browser Compatibility:** Works in Chrome, Firefox, Safari
✅ **Accessibility:** Span tree keyboard navigable, screen reader compatible
✅ **Tests Pass:** All unit, integration, e2e, and playwright tests pass (excluding deleted tests)

---

## Notes

- **Backward Compatibility:** V1 and V2 traces unchanged (no spans), frontend gracefully degrades
- **No External Dependencies:** Uses existing Flask, vanilla JS, CSS - no new libraries
- **Follows Existing Patterns:** Uses established fetch() pattern from `runTest()` in viewer.js
- **Educational Focus:** Span tree makes RAG architecture self-evident from visual structure
- **Production-Ready:** Idempotent seeding ensures safe re-deployments
