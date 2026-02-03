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
