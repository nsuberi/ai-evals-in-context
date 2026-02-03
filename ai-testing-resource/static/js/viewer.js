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

// Version tab switching
function switchVersion(version) {
  // Update URL
  const url = new URL(window.location);
  url.pathname = appUrl(`/viewer/traces/${version}`);
  window.location.href = url.toString();
}

// Test type switching
function switchTestType(testType) {
  window.location.href = appUrl(`/viewer/tests/${testType}`);
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

    // Display response
    responseContainer.innerHTML = `
      <div class="demo-response__text">${escapeHtml(data.text)}</div>
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
