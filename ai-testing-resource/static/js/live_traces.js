/**
 * Live trace viewer with WebSocket integration
 */

class LiveTraceViewer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    this.traces = [];
    this.maxTraces = 100;
    this.socket = null;
    this.connected = false;

    this.init();
  }

  init() {
    // Connect to WebSocket
    this.connect();

    // Set up UI
    this.render();
  }

  connect() {
    // Check if Socket.IO is available
    if (typeof io === 'undefined') {
      console.error('Socket.IO not loaded');
      return;
    }

    this.socket = io('/monitoring');

    this.socket.on('connected', (data) => {
      console.log('Connected to monitoring stream:', data);
      this.connected = true;
      this.updateConnectionStatus(true);
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from monitoring stream');
      this.connected = false;
      this.updateConnectionStatus(false);
    });

    this.socket.on('new_trace', (trace) => {
      this.addTrace(trace);
    });

    this.socket.on('new_alert', (alert) => {
      this.showAlert(alert);
    });

    this.socket.on('metrics_update', (metrics) => {
      this.updateMetrics(metrics);
    });
  }

  addTrace(trace) {
    this.traces.unshift(trace);

    // Limit trace history
    if (this.traces.length > this.maxTraces) {
      this.traces.pop();
    }

    this.render();
  }

  render() {
    if (!this.container) return;

    this.container.innerHTML = this.traces.map(t => this.renderTrace(t)).join('');
  }

  renderTrace(trace) {
    const timestamp = this.formatTime(trace.timestamp);
    const question = this.truncate(trace.question, 60);
    const latencyClass = this.getLatencyClass(trace.latency_ms);
    const feedbackIcon = this.getFeedbackIcon(trace.user_feedback);

    return `
      <div class="trace-item" data-trace-id="${trace.id}">
        <div class="trace-header">
          <span class="trace-time">${timestamp}</span>
          <span class="trace-latency trace-latency--${latencyClass}">${trace.latency_ms}ms</span>
          <span class="trace-feedback">${feedbackIcon}</span>
        </div>
        <div class="trace-question">${question}</div>
        ${trace.anomaly_flags && trace.anomaly_flags.length > 0 ? `
          <div class="trace-anomalies">
            ${trace.anomaly_flags.map(flag => `<span class="anomaly-badge">${flag}</span>`).join('')}
          </div>
        ` : ''}
      </div>
    `;
  }

  formatTime(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  }

  truncate(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }

  getLatencyClass(latency) {
    if (latency < 1000) return 'fast';
    if (latency < 3000) return 'medium';
    return 'slow';
  }

  getFeedbackIcon(feedback) {
    if (feedback === 'positive') return '👍';
    if (feedback === 'negative') return '👎';
    return '-';
  }

  showAlert(alert) {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) return;

    const alertEl = document.createElement('div');
    alertEl.className = `alert alert--${alert.severity}`;
    alertEl.innerHTML = `
      <span class="alert-icon">⚠️</span>
      <div class="alert-content">
        <strong>${alert.category.toUpperCase()}</strong>
        <p>${alert.description}</p>
      </div>
      <button class="alert-close" onclick="this.parentElement.remove()">×</button>
    `;

    alertsContainer.prepend(alertEl);

    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (alertEl.parentElement) {
        alertEl.remove();
      }
    }, 10000);
  }

  updateMetrics(metrics) {
    // Update metric displays
    const updateElement = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value;
    };

    updateElement('metric-trace-count', metrics.trace_count || 0);
    updateElement('metric-error-rate', `${((metrics.error_rate || 0) * 100).toFixed(1)}%`);
    updateElement('metric-latency-p95', `${(metrics.latency_p95 || 0).toFixed(0)}ms`);
    updateElement('metric-satisfaction', `${((metrics.satisfaction_rate || 0) * 100).toFixed(1)}%`);
  }

  updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connection-status');
    if (statusEl) {
      statusEl.textContent = connected ? 'Connected' : 'Disconnected';
      statusEl.className = `connection-status connection-status--${connected ? 'connected' : 'disconnected'}`;
    }
  }

  clearTraces() {
    this.traces = [];
    this.render();
  }

  subscribe(categories) {
    if (this.socket && this.connected) {
      this.socket.emit('subscribe', { categories });
    }
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  const traceContainer = document.getElementById('live-traces');
  if (traceContainer) {
    window.liveTraceViewer = new LiveTraceViewer('live-traces');
  }
});
