/**
 * Line selection functionality for code canvas
 * Supports click, shift-click, keyboard navigation, and URL state management
 */

class LineSelector {
  constructor(codeCanvas) {
    this.canvas = codeCanvas;
    this.gutter = codeCanvas.querySelector('.code-canvas__gutter');
    if (!this.gutter) return; // No gutter, skip initialization

    this.selection = { start: null, end: null };
    this.init();
  }

  init() {
    // Mouse interactions
    this.gutter.addEventListener('click', (e) => this.handleLineClick(e));

    // Keyboard interactions
    document.addEventListener('keydown', (e) => this.handleKeyDown(e));

    // Load selection from URL on page load
    this.loadSelectionFromURL();
  }

  handleLineClick(e) {
    const lineEl = e.target.closest('.gutter__line');
    if (!lineEl) return;

    const lineNum = parseInt(lineEl.dataset.line, 10);

    if (e.shiftKey && this.selection.start !== null) {
      // Extend selection
      this.selection.end = lineNum;
    } else {
      // Start new selection
      this.selection.start = lineNum;
      this.selection.end = lineNum;
    }

    this.updateDisplay();
    this.updateURL();
  }

  handleKeyDown(e) {
    // Only handle shortcuts when canvas is in focus or selection active
    if (!this.selection.start) return;

    switch(e.key) {
      case 'j':
        e.preventDefault();
        this.moveSelection(1, e.shiftKey);
        break;
      case 'k':
        e.preventDefault();
        this.moveSelection(-1, e.shiftKey);
        break;
      case 'y':
        e.preventDefault();
        this.copySelection();
        break;
      case 'Escape':
        e.preventDefault();
        this.clearSelection();
        break;
      case 'g':
        // Go to line (wait for number input)
        if (!this.awaitingLineNumber) {
          e.preventDefault();
          this.awaitingLineNumber = true;
          this.showGoToPrompt();
        }
        break;
    }
  }

  moveSelection(direction, extend) {
    if (this.selection.start === null) {
      // Start from line 1
      this.selection.start = 1;
      this.selection.end = 1;
    } else if (extend) {
      // Extend the end of selection
      this.selection.end = Math.max(1, this.selection.end + direction);
    } else {
      // Move entire selection
      const newLine = Math.max(1, this.selection.start + direction);
      this.selection.start = newLine;
      this.selection.end = newLine;
    }

    this.updateDisplay();
    this.updateURL();
  }

  updateDisplay() {
    // Clear previous selection
    this.gutter.querySelectorAll('.gutter__line--selected').forEach(el => {
      el.classList.remove('gutter__line--selected');
    });

    if (this.selection.start === null) return;

    const start = Math.min(this.selection.start, this.selection.end);
    const end = Math.max(this.selection.start, this.selection.end);

    // Highlight selected lines
    for (let i = start; i <= end; i++) {
      const lineEl = this.gutter.querySelector(`[data-line="${i}"]`);
      if (lineEl) lineEl.classList.add('gutter__line--selected');
    }

    // Update indicator in header
    this.updateIndicator(start, end);

    // Scroll to selection if needed
    const firstSelected = this.gutter.querySelector(`[data-line="${start}"]`);
    if (firstSelected) {
      firstSelected.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  updateIndicator(start, end) {
    let indicator = this.canvas.querySelector('.code-canvas__selection-indicator');

    if (!indicator && this.selection.start !== null) {
      // Create indicator if it doesn't exist
      const header = this.canvas.querySelector('.code-canvas__header');
      if (header) {
        indicator = document.createElement('span');
        indicator.className = 'code-canvas__selection-indicator';
        indicator.innerHTML = 'Lines: <span class="selection-range"></span>';
        header.appendChild(indicator);
      }
    }

    if (indicator) {
      const rangeSpan = indicator.querySelector('.selection-range');
      if (rangeSpan) {
        rangeSpan.textContent = start === end ? start : `${start}-${end}`;
      }
      indicator.style.display = this.selection.start === null ? 'none' : 'inline-flex';
    }
  }

  async copySelection() {
    const { start, end } = this.getNormalizedSelection();
    const lines = this.getCodeLines(start, end);

    try {
      await navigator.clipboard.writeText(lines);
      this.showCopyFeedback();
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }

  getCodeLines(start, end) {
    const codeEl = this.canvas.querySelector('.code-canvas__code code');
    if (!codeEl) return '';

    const lines = codeEl.textContent.split('\n');
    return lines.slice(start - 1, end).join('\n');
  }

  getNormalizedSelection() {
    if (this.selection.start === null) {
      return { start: 1, end: 1 };
    }
    return {
      start: Math.min(this.selection.start, this.selection.end),
      end: Math.max(this.selection.start, this.selection.end)
    };
  }

  shareSelection() {
    const { start, end } = this.getNormalizedSelection();
    const file = this.canvas.dataset.file;
    const url = new URL(window.location.href);

    url.searchParams.set('file', file);
    url.searchParams.set('L', start === end ? start : `${start}-${end}`);

    navigator.clipboard.writeText(url.toString());
    this.showCopyFeedback('Link copied!');
  }

  clearSelection() {
    this.selection.start = null;
    this.selection.end = null;
    this.updateDisplay();
    this.clearURL();
  }

  updateURL() {
    const { start, end } = this.getNormalizedSelection();
    const url = new URL(window.location.href);
    url.searchParams.set('L', start === end ? start : `${start}-${end}`);
    window.history.replaceState({}, '', url);
  }

  clearURL() {
    const url = new URL(window.location.href);
    url.searchParams.delete('L');
    window.history.replaceState({}, '', url);
  }

  loadSelectionFromURL() {
    const params = new URLSearchParams(window.location.search);
    const lineParam = params.get('L');

    if (lineParam) {
      if (lineParam.includes('-')) {
        const [start, end] = lineParam.split('-').map(n => parseInt(n, 10));
        this.selection.start = start;
        this.selection.end = end;
      } else {
        const line = parseInt(lineParam, 10);
        this.selection.start = line;
        this.selection.end = line;
      }
      this.updateDisplay();
    }
  }

  showGoToPrompt() {
    const lineNum = prompt('Go to line:');
    this.awaitingLineNumber = false;

    if (lineNum) {
      const line = parseInt(lineNum, 10);
      if (!isNaN(line)) {
        this.selection.start = line;
        this.selection.end = line;
        this.updateDisplay();
        this.updateURL();
      }
    }
  }

  showCopyFeedback(message = 'Copied!') {
    const indicator = this.canvas.querySelector('.code-canvas__selection-indicator');
    if (!indicator) return;

    const originalText = indicator.innerHTML;
    indicator.innerHTML = `<span style="color: var(--color-success);">✓ ${message}</span>`;

    setTimeout(() => {
      indicator.innerHTML = originalText;
    }, 2000);
  }
}

// Initialize line selectors for all code canvases on page load
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.code-canvas').forEach(canvas => {
    new LineSelector(canvas);
  });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LineSelector;
}
