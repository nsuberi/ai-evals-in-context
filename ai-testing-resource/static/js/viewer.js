/**
 * AI Testing Resource - Viewer JavaScript
 */

// Get the application root prefix (set by template)
const APP_ROOT = window.APP_ROOT || '';

// Helper to build prefixed URLs
function appUrl(path) {
  return APP_ROOT + path;
}

// Toggle collapsible sections
function toggleCollapsible(element) {
  element.classList.toggle('collapsible--open');
}

// Run a test and display results
async function runTest(testId) {
  const canvas = document.querySelector(`[data-test-id="${testId}"]`);
  const button = canvas.querySelector('.run-button');

  // Set loading state
  button.classList.add('run-button--loading');
  button.innerHTML = '<span>&#8987;</span> Running...';

  // Remove any existing result
  const existingResult = canvas.querySelector('.code-canvas__result');
  if (existingResult) {
    existingResult.remove();
  }

  try {
    const response = await fetch(appUrl(`/viewer/tests/run/${testId}`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    // Create result element
    const resultDiv = document.createElement('div');
    resultDiv.className = `code-canvas__result code-canvas__result--${data.status}`;
    resultDiv.textContent = data.output;

    // Add to canvas
    canvas.appendChild(resultDiv);

  } catch (error) {
    // Create error result
    const resultDiv = document.createElement('div');
    resultDiv.className = 'code-canvas__result code-canvas__result--fail';
    resultDiv.textContent = `Error: ${error.message}`;
    canvas.appendChild(resultDiv);
  } finally {
    // Reset button
    button.classList.remove('run-button--loading');
    button.innerHTML = '<span>&#9654;</span> Run';
  }
}

// Version tab switching (now handled by narrative phases)
// Legacy viewer routes removed - keeping function signature for compatibility
function switchVersion(version) {
  console.warn('switchVersion() called but viewer routes are removed');
}

// Test type switching (now handled by narrative phases)
// Legacy viewer routes removed - keeping function signature for compatibility
function switchTestType(testType) {
  console.warn('switchTestType() called but viewer routes are removed');
}

// Test selection
function selectTest(testId) {
  const url = new URL(window.location);
  url.searchParams.set('test', testId);
  window.location.href = url.toString();
}

// Trace selection
function selectTrace(traceId) {
  const url = new URL(window.location);
  url.searchParams.set('trace', traceId);
  window.location.href = url.toString();
}

// Demo form handling
async function submitDemoForm(event) {
  event.preventDefault();

  const form = event.target;
  const question = form.querySelector('[name="question"]').value;
  const version = form.querySelector('[name="version"]').value;
  const submitBtn = form.querySelector('.demo-form__submit');
  const responseContainer = document.getElementById('demo-response');

  // Set loading state
  submitBtn.textContent = 'Thinking...';
  submitBtn.disabled = true;

  try {
    const response = await fetch(appUrl('/ask'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question, version })
    });

    const data = await response.json();

    // Display response (HTML from server-side markdown conversion)
    responseContainer.innerHTML = `
      <div class="demo-response__text">${data.text}</div>
      <div class="demo-response__metadata">
        <span class="demo-response__meta-item">
          <strong>Latency:</strong> ${data.metadata.latency_ms}ms
        </span>
        <span class="demo-response__meta-item">
          <strong>Tokens:</strong> ${data.metadata.total_tokens}
        </span>
      </div>
      ${data.sources && data.sources.length > 0 ? `
        <div class="demo-response__sources">
          <div class="demo-response__sources-title">Sources</div>
          ${data.sources.map(s => `<div>${escapeHtml(s.title)}</div>`).join('')}
        </div>
      ` : ''}
    `;

    // Render trace panel
    renderTracePanel(data.trace);
  } catch (error) {
    responseContainer.innerHTML = `
      <div class="demo-response__text" style="color: var(--color-error);">
        Error: ${escapeHtml(error.message)}
      </div>
    `;
  } finally {
    submitBtn.textContent = 'Ask';
    submitBtn.disabled = false;
  }
}

// Utility: escape HTML
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Toggle trace panel visibility
function toggleTracePanel() {
  const panel = document.getElementById('trace-panel');
  panel.classList.toggle('trace-panel--open');
}

// Render the KB trace panel
function renderTracePanel(trace) {
  const panel = document.getElementById('trace-panel');
  const content = document.getElementById('trace-panel__content');

  if (!panel || !content || !trace) return;

  // Show the panel
  panel.style.display = 'block';

  // Check if KB is not in use
  if (trace.not_in_use) {
    content.innerHTML = `
      <div class="trace-step">
        <div class="trace-step__header">
          <span class="trace-step__icon">&#128683;</span>
          <span class="trace-step__title">Not in use</span>
        </div>
        <div class="trace-step__body">
          <p class="trace-step__reason">${escapeHtml(trace.reason)}</p>
          <p class="trace-step__hint">Switch to <strong>V3 - RAG</strong> to see the knowledge base pipeline in action.</p>
        </div>
      </div>
    `;
    return;
  }

  // V3 full pipeline trace
  content.innerHTML = `
    <!-- Step 1: Query -->
    <div class="trace-step">
      <div class="trace-step__header">
        <span class="trace-step__number">1</span>
        <span class="trace-step__title">Query</span>
      </div>
      <div class="trace-step__body">
        <code class="trace-step__code">${escapeHtml(trace.query)}</code>
      </div>
    </div>

    <!-- Step 2: Retrieved Documents -->
    <div class="trace-step">
      <div class="trace-step__header">
        <span class="trace-step__number">2</span>
        <span class="trace-step__title">Retrieved Documents (${trace.retrieved_docs?.length || 0})</span>
      </div>
      <div class="trace-step__body">
        ${trace.retrieved_docs?.map(doc => `
          <div class="trace-doc">
            <div class="trace-doc__header">
              <span class="trace-doc__title">${escapeHtml(doc.title)}</span>
              <span class="trace-doc__distance">distance: ${doc.distance}</span>
            </div>
            <div class="trace-doc__content">${escapeHtml(doc.content)}</div>
          </div>
        `).join('') || '<p>No documents retrieved</p>'}
      </div>
    </div>

    <!-- Step 3: Formatted Context -->
    <div class="trace-step">
      <div class="trace-step__header trace-step__header--collapsible" onclick="this.parentElement.classList.toggle('trace-step--expanded')">
        <span class="trace-step__number">3</span>
        <span class="trace-step__title">Formatted Context</span>
        <span class="trace-step__expand">&#9660;</span>
      </div>
      <div class="trace-step__body trace-step__body--collapsible">
        <pre class="trace-step__pre">${escapeHtml(trace.formatted_context)}</pre>
      </div>
    </div>

    <!-- Step 4: System Prompt -->
    <div class="trace-step">
      <div class="trace-step__header trace-step__header--collapsible" onclick="this.parentElement.classList.toggle('trace-step--expanded')">
        <span class="trace-step__number">4</span>
        <span class="trace-step__title">System Prompt</span>
        <span class="trace-step__expand">&#9660;</span>
      </div>
      <div class="trace-step__body trace-step__body--collapsible">
        <pre class="trace-step__pre">${escapeHtml(trace.system_prompt)}</pre>
      </div>
    </div>

    <!-- Step 5: User Message -->
    <div class="trace-step">
      <div class="trace-step__header">
        <span class="trace-step__number">5</span>
        <span class="trace-step__title">User Message</span>
      </div>
      <div class="trace-step__body">
        <code class="trace-step__code">${escapeHtml(trace.user_message)}</code>
      </div>
    </div>
  `;
}

// ──────────────────────────────────────────────────────────────────
// Dynamic Trace Switching (Phase 4)
// ──────────────────────────────────────────────────────────────────

/**
 * Switch to a different trace without page reload
 */
async function switchTrace(version, traceId) {
  const mainContent = document.querySelector('.content-primary');
  const sidebarItems = document.querySelectorAll('.sidebar__item');

  if (!mainContent) return;

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

/**
 * Render complete trace detail (response + spans + metadata)
 */
function renderTraceDetail(data) {
  const mainContent = document.querySelector('.content-primary');
  if (!mainContent) return;

  const versionColor = getVersionColor(data.version);

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
        <span class="code-canvas__badge" style="background: var(--color-${versionColor});">
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

    <!-- Secondary Content: Prompt + Metadata -->
    <div class="content-secondary">
      ${renderPromptCollapsible(data.trace_detail.prompt)}
      ${renderMetadata(data.trace_detail)}
    </div>
  `;

  mainContent.innerHTML = html;
}

/**
 * Render LangSmith-style span tree visualization
 */
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

/**
 * Color mapping for span types
 */
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

/**
 * Toggle span expansion
 */
function toggleSpan(spanElement) {
  spanElement.classList.toggle('span-item--expanded');
}

/**
 * Get version color for badges
 */
function getVersionColor(version) {
  const colors = {
    v1: 'error',
    v2: 'warning',
    v3: 'success'
  };
  return colors[version] || 'chrome-text';
}

/**
 * Render annotation footnotes
 */
function renderAnnotationFootnotes(annotations) {
  if (!annotations || annotations.length === 0) return '';

  const footnotes = annotations.map((ann, idx) => {
    let severityClass = 'ann--info';
    if (ann.severity === 'error') severityClass = 'ann--error';
    if (ann.severity === 'warning') severityClass = 'ann--warning';
    if (ann.severity === 'success') severityClass = 'ann--success';

    return `
      <div class="ann ${severityClass}">
        <strong>${idx + 1}.</strong> ${escapeHtml(ann.text)}
      </div>
    `;
  }).join('');

  return `<div class="code-canvas__annotations">${footnotes}</div>`;
}

/**
 * Render prompt collapsible
 */
function renderPromptCollapsible(prompt) {
  if (!prompt) return '';
  return `
    <div class="collapsible">
      <div class="collapsible__header" onclick="toggleCollapsible(this.parentElement)">
        <span class="collapsible__title">System Prompt</span>
        <span class="collapsible__icon">▼</span>
      </div>
      <div class="collapsible__body">
        <pre class="collapsible__code">${escapeHtml(prompt)}</pre>
      </div>
    </div>
  `;
}

/**
 * Render metadata section
 */
function renderMetadata(trace) {
  return `
    <div class="trace-metadata">
      <div class="trace-metadata__item">
        <span class="trace-metadata__label">Latency</span>
        <span class="trace-metadata__value">${trace.latency_ms}ms</span>
      </div>
      <div class="trace-metadata__item">
        <span class="trace-metadata__label">Tokens</span>
        <span class="trace-metadata__value">${trace.tokens.prompt + trace.tokens.completion}</span>
      </div>
      ${trace.sources && trace.sources.length > 0 ? `
        <div class="trace-metadata__item">
          <span class="trace-metadata__label">Sources</span>
          <span class="trace-metadata__value">${trace.sources.map(s => escapeHtml(s.title)).join(', ')}</span>
        </div>
      ` : ''}
    </div>
  `;
}

// Browser history support
window.addEventListener('popstate', (event) => {
  if (event.state && event.state.traceId) {
    switchTrace(event.state.version, event.state.traceId);
  }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  // Add click handlers to sidebar items
  document.querySelectorAll('.sidebar__item').forEach(item => {
    item.addEventListener('click', (e) => {
      // Let the link navigate naturally
    });
  });

  // Initialize demo form if present
  const demoForm = document.querySelector('.demo-form');
  if (demoForm) {
    demoForm.addEventListener('submit', submitDemoForm);
  }
});
