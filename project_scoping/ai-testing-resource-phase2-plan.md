# Implementation Plan: AI Testing Resource — Phase 2

## Overview

Phase 2 extends the AI Testing Resource with production-grade features for enterprise deployment:

1. **Enhanced Code Viewer** — Line numbers, syntax highlighting, and interactive line selection
2. **Test Summary Report (TSR)** — Comprehensive test records with version tracking and AI eval history
3. **CI/CD Integration** — Automated go/no-go gates for deployments
4. **Governance Viewer** — Audit-ready interface for compliance verification
5. **Production Monitoring** — Live trace monitoring and interaction metrics

These features transform the educational resource into a production system that enables faster, safer experimentation while maintaining governance and compliance requirements.

---

## Architecture Diagrams

### CI/CD Pipeline Architecture

```
    Developer                                                           Production
        │                                                                   ▲
        │ git push                                                          │
        ▼                                                                   │
┌───────────────┐    ┌──────────────────────────────────────────────────────┴────────┐
│   Git Repo    │    │                    CI/CD Pipeline                              │
│               │    │                                                                 │
│  ┌─────────┐  │    │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────────┐│
│  │Codebase │──┼────┼─▶│  Build  │──▶│  Test   │──▶│ Generate│──▶│   Go/No-Go     ││
│  └─────────┘  │    │  │         │   │  Suite  │   │   TSR   │   │     Gate        ││
│  ┌─────────┐  │    │  └─────────┘   └─────────┘   └────┬────┘   └───────┬─────────┘│
│  │Testbase │──┼────┼───────────────────────────────────│                │          │
│  └─────────┘  │    │                                   │                │          │
│  ┌─────────┐  │    │                                   ▼                ▼          │
│  │ Prompts │──┼────┼─────────────────────────────┬─────────────────────────────┐  │
│  └─────────┘  │    │                             │      TSR Database           │  │
└───────────────┘    │                             │  ┌─────────────────────┐    │  │
                     │                             │  │ POST /api/tsr       │    │  │
                     │                             │  │ GET  /api/tsr/{id}/ │    │  │
                     │                             │  │      go-no-go       │    │  │
                     │                             │  └─────────────────────┘    │  │
                     │                             └─────────────────────────────┘  │
                     │                                          │                    │
                     │                    ┌─────────────────────┴────────────┐      │
                     │                    │                                   │      │
                     │                    ▼                                   ▼      │
                     │            ┌──────────────┐                   ┌──────────────┐│
                     │            │  GO: Deploy  │                   │ NO-GO: Block ││
                     │            │  to Staging  │                   │  Notify Team ││
                     │            └──────┬───────┘                   └──────────────┘│
                     │                   │                                           │
                     │                   ▼                                           │
                     │            ┌──────────────┐         ┌──────────────────────┐ │
                     │            │  Production  │◀────────│  Manual Approval     │ │
                     │            │  Deployment  │         │  (if required)       │ │
                     │            └──────────────┘         └──────────────────────┘ │
                     └───────────────────────────────────────────────────────────────┘
```

### Persona Workflow: Before vs. After

```
BEFORE (Manual Process):
═══════════════════════

Developer ──▶ PR Review ──▶ QA Lead ──▶ Manual Test ──▶ Test Report ──▶ Release Mgr
    │            │             │            │              │              │
    ▼            ▼             ▼            ▼              ▼              ▼
  1 day      2-3 days       1 day      3-5 days        1 day          1 day
                                                                         │
                                                                         ▼
Security Review ──▶ Change Advisory Board ──▶ Production Deploy
      │                      │                        │
      ▼                      ▼                        ▼
   2 days               Weekly meeting             Scheduled window

Total: 12-20 days, 6+ handoffs, multiple meetings

═══════════════════════════════════════════════════════════════════════════════════════

AFTER (Automated TSR + Go/No-Go):
═════════════════════════════════

Developer ──▶ PR (triggers CI) ──▶ Automated Tests ──▶ TSR Generated ──▶ Go/No-Go Gate
    │              │                     │                  │                │
    ▼              ▼                     ▼                  ▼                ▼
  Code          Minutes              30-60 min          Automatic        Automatic
                                                                            │
                                    ┌───────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
              GO: Auto-deploy              NO-GO: Blocked
              to Staging                   with clear reason
                    │                               │
                    ▼                               ▼
            Staging Smoke Tests            Developer fixes
            (automated, 10 min)            (immediate feedback)
                    │
                    ▼
            Production Deploy
            (auto or 1-click approval)

Total: 1-2 hours (if passing), 1 handoff (optional approval)
```

### Personas

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Developer     │  │   Tech Lead     │  │  Release Mgr    │  │ Governance/     │
│                 │  │                 │  │                 │  │ Audit Official  │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Writes code   │  │ • Reviews PRs   │  │ • Monitors TSRs │  │ • Reviews TSR   │
│ • Writes tests  │  │ • Sets go/no-go │  │ • Approves prod │  │   history       │
│ • Sees instant  │  │   thresholds    │  │   deploys when  │  │ • Verifies test │
│   TSR feedback  │  │ • Reviews       │  │   required      │  │   coverage      │
│ • Fixes issues  │  │   failure modes │  │ • Tracks DORA   │  │ • Audits AI     │
│   immediately   │  │                 │  │   metrics       │  │   eval history  │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### DORA Metrics & MTTR Connection

```
MEAN TIME TO RECOVERY (MTTR):
════════════════════════════

Traditional MTTR: 5-7 days
┌──────────────────────────────────────────────────────────────────────────────────┐
│  Incident     Detection    Diagnosis    Fix Dev    Testing    Approval    Deploy │
│  Occurs  ──▶  (monitors) ──▶ (manual) ──▶ (hours) ──▶ (days) ──▶ (days) ──▶ (hrs)│
└──────────────────────────────────────────────────────────────────────────────────┘

With TSR + Automated Go/No-Go - MTTR: 4-8 hours
┌──────────────────────────────────────────────────────────────────────────────────┐
│  Incident     Detection    Diagnosis    Fix Dev    TSR Gate    Deploy            │
│  Occurs  ──▶  (monitors) ──▶ (traces!) ──▶ (hours) ──▶ (auto) ──▶ (auto)         │
│                  │              │                       │                         │
│            Production      Annotated               Automated                      │
│            monitoring      traces show             verification                   │
│            catches it      exact failure                                          │
└──────────────────────────────────────────────────────────────────────────────────┘

WHY THIS WORKS:

1. FASTER DETECTION - Production trace monitoring catches AI behavior drift
2. FASTER DIAGNOSIS - Annotated traces show EXACT failure mode  
3. FASTER VERIFICATION - Automated test suite + evals run in minutes
4. SAFER EXPERIMENTATION - Fast feedback = more experiments = faster learning

ORGANIZATIONAL RISK REDUCTION:
═════════════════════════════

   Risk = Probability(Failure) × Impact × Time_to_Recover
   
   TSR reduces all three factors:
   • Probability: Comprehensive automated testing catches issues early
   • Impact: Faster detection limits blast radius
   • Time_to_Recover: Automated pipeline eliminates handoffs
   
   Result: Organization can ship MORE frequently with LESS risk per deployment
```

---

## File Structure Additions

```
ai-testing-resource/
├── ... (existing Phase 1 structure) ...
│
├── viewer/
│   ├── ... (existing) ...
│   ├── code_selection.py         # Line selection logic
│   ├── compliance.py             # Compliance checking
│   ├── pdf_export.py             # PDF generation
│   │
│   ├── templates/
│   │   ├── components/
│   │   │   ├── code_canvas.html  # Enhanced with line numbers/selection
│   │   │   └── line_gutter.html  # Line number gutter component
│   │   │
│   │   ├── governance/
│   │   │   ├── dashboard.html    # TSR list view
│   │   │   ├── tsr_detail.html   # Full TSR view
│   │   │   ├── comparison.html   # Side-by-side TSR comparison
│   │   │   └── compliance.html   # Compliance checklist
│   │   │
│   │   └── monitoring/
│   │       ├── traces.html       # Production trace monitoring
│   │       └── metrics.html      # Interaction metrics
│   │
│   └── static/
│       ├── css/
│       │   └── governance.css    # Governance portal branding
│       └── js/
│           ├── line_selection.js # Line selection interactions
│           ├── live_traces.js    # WebSocket trace feed
│           └── charts.js         # Chart.js configurations
│
├── tsr/                          # TSR subsystem
│   ├── __init__.py
│   ├── models.py                 # TSR data models
│   ├── generator.py              # TSR generation from test results
│   ├── rules.py                  # Go/No-Go rules engine
│   ├── api.py                    # REST API routes
│   ├── repository.py             # Database access layer
│   └── database.py               # SQLAlchemy models
│
├── monitoring/                   # Production monitoring
│   ├── __init__.py
│   ├── models.py                 # Trace and metrics models
│   ├── collector.py              # Trace collection service
│   ├── anomaly.py                # Anomaly detection
│   ├── metrics.py                # Metric aggregation
│   ├── drift.py                  # Drift detection
│   └── stream.py                 # WebSocket streaming
│
├── scripts/
│   ├── generate_tsr.py           # CLI for TSR generation
│   └── setup_tsr_db.py           # Database setup
│
└── migrations/
    └── versions/
        └── 001_tsr_tables.py     # TSR database migration
```

---

## Phase 6: Enhanced Code Viewer

### Line Selection Data Model

```python
# viewer/code_selection.py
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode

@dataclass
class LineSelection:
    """Represents selected lines in a code file"""
    file_path: str
    start_line: int
    end_line: int
    commit_sha: Optional[str] = None
    
    def to_url_params(self) -> str:
        """Generate URL parameters for this selection"""
        params = {
            'file': self.file_path,
            'L': f"{self.start_line}-{self.end_line}" if self.start_line != self.end_line 
                 else str(self.start_line)
        }
        if self.commit_sha:
            params['ref'] = self.commit_sha
        return urlencode(params)
    
    @classmethod
    def from_url_params(cls, params: dict) -> Optional['LineSelection']:
        """Parse selection from URL query parameters"""
        if 'file' not in params or 'L' not in params:
            return None
        
        file_path = params['file'][0] if isinstance(params['file'], list) else params['file']
        line_spec = params['L'][0] if isinstance(params['L'], list) else params['L']
        
        if '-' in line_spec:
            start, end = map(int, line_spec.split('-'))
        else:
            start = end = int(line_spec)
        
        return cls(file_path=file_path, start_line=start, end_line=end,
                   commit_sha=params.get('ref', [None])[0])

def get_line_content(file_path: str, start_line: int, end_line: int) -> str:
    """Extract specific lines from a file"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return ''.join(lines[start_line - 1:end_line])
```

### Line Selection CSS

```css
/* Add to static/css/design-system.css */

.code-canvas__body {
  display: flex;
  overflow-x: auto;
}

.code-canvas__gutter {
  flex-shrink: 0;
  padding: var(--space-lg) 0;
  background: var(--color-canvas-border);
  border-right: 1px solid #d1d5db;
  user-select: none;
  min-width: 3.5rem;
  text-align: right;
}

.gutter__line {
  padding: 0 var(--space-md);
  font-family: var(--font-code);
  font-size: 13px;
  line-height: 1.7;
  color: #9ca3af;
  cursor: pointer;
}

.gutter__line:hover {
  color: #4b5563;
  background: rgba(0, 0, 0, 0.05);
}

.gutter__line--selected {
  background: var(--color-accent);
  color: white;
}

.code-canvas__selection-indicator {
  font-size: 0.8125rem;
  color: #6b7280;
}

.code-canvas__selection-indicator .selection-range {
  font-weight: 600;
  color: var(--color-accent);
}
```

### Keyboard Navigation

| Key | Action |
|-----|--------|
| `j` | Move selection down |
| `k` | Move selection up |
| `Shift+j` | Extend selection down |
| `Shift+k` | Extend selection up |
| `y` | Yank (copy) selection |
| `g` + number | Go to line |
| `Escape` | Clear selection |

### Line Selection JavaScript

```javascript
// viewer/static/js/line_selection.js

class LineSelector {
  constructor(codeCanvas) {
    this.canvas = codeCanvas;
    this.gutter = codeCanvas.querySelector('.code-canvas__gutter');
    this.selection = { start: null, end: null };
    this.init();
  }
  
  init() {
    this.gutter.addEventListener('click', (e) => this.handleLineClick(e));
    document.addEventListener('keydown', (e) => this.handleKeyDown(e));
    this.loadSelectionFromURL();
  }
  
  handleLineClick(e) {
    const lineEl = e.target.closest('.gutter__line');
    if (!lineEl) return;
    
    const lineNum = parseInt(lineEl.dataset.line, 10);
    
    if (e.shiftKey && this.selection.start !== null) {
      this.selection.end = lineNum;
    } else {
      this.selection.start = lineNum;
      this.selection.end = lineNum;
    }
    
    this.updateDisplay();
  }
  
  handleKeyDown(e) {
    switch(e.key) {
      case 'j': this.moveSelection(1, e.shiftKey); break;
      case 'k': this.moveSelection(-1, e.shiftKey); break;
      case 'y': this.copySelection(); break;
      case 'Escape': this.clearSelection(); break;
    }
  }
  
  moveSelection(direction, extend) {
    if (this.selection.start === null) {
      this.selection.start = 1;
      this.selection.end = 1;
    } else if (extend) {
      this.selection.end += direction;
    } else {
      this.selection.start += direction;
      this.selection.end = this.selection.start;
    }
    this.updateDisplay();
  }
  
  updateDisplay() {
    // Clear previous selection
    this.gutter.querySelectorAll('.gutter__line--selected').forEach(el => {
      el.classList.remove('gutter__line--selected');
    });
    
    if (this.selection.start === null) return;
    
    const start = Math.min(this.selection.start, this.selection.end);
    const end = Math.max(this.selection.start, this.selection.end);
    
    for (let i = start; i <= end; i++) {
      const lineEl = this.gutter.querySelector(`[data-line="${i}"]`);
      if (lineEl) lineEl.classList.add('gutter__line--selected');
    }
    
    // Update indicator
    const indicator = this.canvas.querySelector('.selection-range');
    if (indicator) {
      indicator.textContent = start === end ? start : `${start}-${end}`;
    }
  }
  
  async copySelection() {
    const { start, end } = this.getNormalizedSelection();
    const lines = this.getCodeLines(start, end);
    await navigator.clipboard.writeText(lines);
  }
  
  shareSelection() {
    const { start, end } = this.getNormalizedSelection();
    const file = this.canvas.dataset.file;
    const url = new URL(window.location.href);
    url.searchParams.set('file', file);
    url.searchParams.set('L', start === end ? start : `${start}-${end}`);
    navigator.clipboard.writeText(url.toString());
  }
}

// Initialize
document.querySelectorAll('.code-canvas').forEach(canvas => {
  new LineSelector(canvas);
});
```

---

## Phase 7: Test Summary Report Model

### Core TSR Data Model

```python
# tsr/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
import uuid

class GoNoGoDecision(Enum):
    GO = "go"
    NO_GO = "no_go"
    PENDING_REVIEW = "pending_review"

class TestType(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    ACCEPTANCE = "acceptance"
    EVALS = "evals"
    SECURITY = "security"
    PERFORMANCE = "performance"

@dataclass
class VersionManifest:
    """Tracks git commits for all versioned components"""
    codebase_sha: str
    codebase_branch: str
    codebase_repo: str
    testbase_sha: str
    prompts_sha: str
    prompts_version: Optional[str] = None  # Semantic version like "v2.1.0"

@dataclass
class TestTypeResult:
    """Results for a single test type"""
    test_type: TestType
    total: int
    passed: int
    failed: int
    skipped: int
    duration_ms: int
    failure_details: List[dict] = field(default_factory=list)
    
    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total > 0 else 1.0

@dataclass
class FailureMode:
    """A discovered failure mode in AI behavior"""
    id: str
    name: str
    description: str
    severity: str  # critical, major, minor
    category: str  # accuracy, format, safety, performance, grounding
    discovered_in_iteration: int
    resolution_status: str = "open"  # open, fixed, wont_fix, accepted_risk

@dataclass 
class EvalIterationSummary:
    """Summary of a single eval iteration (e.g., V1, V2, V3)"""
    iteration: int
    version_name: str  # "V1 Verbose", "V2 No RAG", "V3 RAG"
    prompt_version: str
    outcome: str  # failed, improved, passed
    metrics: dict  # accuracy, avg_length, grounding_score, latency
    failure_modes: List[FailureMode] = field(default_factory=list)
    fixes_applied: List[dict] = field(default_factory=list)

@dataclass
class RequirementCoverage:
    """Coverage status for a single requirement"""
    requirement_id: str
    requirement_text: str
    test_ids: List[str]
    coverage_status: str  # covered, partial, uncovered
    verification_status: str  # verified, failed, not_run

@dataclass
class TestSummaryReport:
    """Complete Test Summary Report"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    triggered_by: str = "manual"
    environment: str = "test"
    
    versions: VersionManifest = None
    test_results: List[TestTypeResult] = field(default_factory=list)
    eval_iterations: List[EvalIterationSummary] = field(default_factory=list)
    requirement_coverage: List[RequirementCoverage] = field(default_factory=list)
    
    overall_status: str = "passed"
    go_no_go_decision: GoNoGoDecision = GoNoGoDecision.PENDING_REVIEW
    decision_reason: str = ""
    blocking_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    manual_approval_required: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
```

---

## Phase 8: Go/No-Go Rules Engine

### Default Rules Configuration

```python
# tsr/rules.py
DEFAULT_RULES = {
    "blocking_conditions": [
        {"type": "test_type_all_fail", "test_type": "security", 
         "message": "Security tests must all pass"},
        {"type": "test_type_all_fail", "test_type": "unit",
         "message": "Unit tests must all pass"},
        {"type": "eval_metric_below", "metric": "accuracy", "threshold": 0.85,
         "message": "Eval accuracy below 85%"},
        {"type": "unresolved_failure_mode", "severity": "critical",
         "message": "Critical failure mode unresolved"}
    ],
    "warning_conditions": [
        {"type": "eval_metric_below", "metric": "grounding_score", "threshold": 0.90,
         "message": "Grounding score below 90%"},
        {"type": "test_failure_rate", "test_type": "performance", "threshold": 0.05,
         "message": "Performance test failure rate above 5%"}
    ],
    "required_coverage": {
        "requirements": 0.95,
        "code": 0.80
    },
    "eval_requirements": {
        "min_iterations_documented": 1,
        "latest_iteration_must_pass": True
    }
}
```

### Go/No-Go Evaluator

```python
class GoNoGoEvaluator:
    def evaluate(self, tsr: TestSummaryReport) -> tuple:
        """Returns (decision, reason, blocking_issues, warnings)"""
        blocking = []
        warnings = []
        
        # Check test results
        for result in tsr.test_results:
            if result.test_type.value in ['security', 'unit'] and result.failed > 0:
                blocking.append(f"{result.test_type.value}: {result.failed} failed")
        
        # Check eval metrics
        if tsr.eval_iterations:
            latest = tsr.eval_iterations[-1]
            if latest.metrics.get('accuracy', 0) < 0.85:
                blocking.append(f"Accuracy {latest.metrics['accuracy']:.1%} < 85%")
            if latest.outcome != 'passed':
                blocking.append("Latest eval iteration did not pass")
        
        # Check requirement coverage
        if tsr.requirement_coverage:
            verified = sum(1 for r in tsr.requirement_coverage 
                          if r.verification_status == 'verified')
            rate = verified / len(tsr.requirement_coverage)
            if rate < 0.95:
                blocking.append(f"Requirement coverage {rate:.1%} < 95%")
        
        # Determine decision
        if blocking:
            return (GoNoGoDecision.NO_GO, f"{len(blocking)} blocking issue(s)", 
                    blocking, warnings)
        return (GoNoGoDecision.GO, "All checks passed", [], warnings)
```

---

## Phase 9: TSR Database & API

### Database Schema

```sql
CREATE TABLE test_summary_reports (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    triggered_by VARCHAR(100) NOT NULL,
    environment VARCHAR(50) NOT NULL,
    overall_status VARCHAR(20) NOT NULL,
    go_no_go_decision VARCHAR(20) NOT NULL,
    decision_reason TEXT,
    blocking_issues JSONB DEFAULT '[]',
    warnings JSONB DEFAULT '[]',
    
    -- Version manifest
    codebase_sha VARCHAR(40) NOT NULL,
    codebase_branch VARCHAR(255),
    testbase_sha VARCHAR(40) NOT NULL,
    prompts_sha VARCHAR(40) NOT NULL,
    prompts_version VARCHAR(50),
    
    -- Approval
    manual_approval_required BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(255),
    approved_at TIMESTAMPTZ
);

CREATE INDEX idx_tsr_created_at ON test_summary_reports(created_at DESC);
CREATE INDEX idx_tsr_codebase_sha ON test_summary_reports(codebase_sha);
CREATE INDEX idx_tsr_decision ON test_summary_reports(go_no_go_decision);

CREATE TABLE tsr_test_results (
    id UUID PRIMARY KEY,
    tsr_id UUID REFERENCES test_summary_reports(id),
    test_type VARCHAR(50) NOT NULL,
    total INT NOT NULL,
    passed INT NOT NULL,
    failed INT NOT NULL,
    skipped INT NOT NULL,
    duration_ms INT NOT NULL,
    failure_details JSONB
);

CREATE TABLE tsr_eval_iterations (
    id UUID PRIMARY KEY,
    tsr_id UUID REFERENCES test_summary_reports(id),
    iteration INT NOT NULL,
    version_name VARCHAR(100) NOT NULL,
    prompt_version VARCHAR(50),
    outcome VARCHAR(20) NOT NULL,
    metrics JSONB NOT NULL,
    failure_modes JSONB,
    fixes_applied JSONB
);

CREATE TABLE tsr_requirement_coverage (
    id UUID PRIMARY KEY,
    tsr_id UUID REFERENCES test_summary_reports(id),
    requirement_id VARCHAR(50) NOT NULL,
    requirement_text TEXT NOT NULL,
    test_ids JSONB NOT NULL,
    coverage_status VARCHAR(20) NOT NULL,
    verification_status VARCHAR(20) NOT NULL
);
```

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tsr` | Create new TSR |
| GET | `/api/tsr/{id}` | Get TSR by ID |
| GET | `/api/tsr/latest` | Get most recent TSR |
| GET | `/api/tsr/{id}/go-no-go` | Get deployment decision (for CI/CD) |
| POST | `/api/tsr/{id}/approve` | Manual approval |
| GET | `/api/tsr/query` | Query with filters |

### API Implementation

```python
# tsr/api.py
from flask import Blueprint, request, jsonify
from .repository import TSRRepository
from .models import TestSummaryReport, GoNoGoDecision

tsr_api = Blueprint('tsr_api', __name__, url_prefix='/api/tsr')

@tsr_api.route('', methods=['POST'])
def create_tsr():
    data = request.get_json()
    tsr = TestSummaryReport.from_dict(data)
    repo.save(tsr)
    return jsonify({
        'id': tsr.id,
        'go_no_go_decision': tsr.go_no_go_decision.value
    }), 201

@tsr_api.route('/<tsr_id>/go-no-go', methods=['GET'])
def get_go_no_go(tsr_id: str):
    """Used by CI/CD pipelines to gate deployments"""
    tsr = repo.get_by_id(tsr_id)
    if not tsr:
        return jsonify({'error': 'TSR not found'}), 404
    
    return jsonify({
        'decision': tsr.go_no_go_decision.value,
        'reason': tsr.decision_reason,
        'blocking_issues': tsr.blocking_issues,
        'warnings': tsr.warnings,
        'manual_approval_required': tsr.manual_approval_required
    })

@tsr_api.route('/<tsr_id>/approve', methods=['POST'])
def approve_tsr(tsr_id: str):
    data = request.get_json()
    tsr = repo.get_by_id(tsr_id)
    
    tsr.approved_by = data.get('approved_by')
    tsr.approved_at = datetime.utcnow()
    
    if tsr.go_no_go_decision == GoNoGoDecision.PENDING_REVIEW:
        tsr.go_no_go_decision = GoNoGoDecision.GO
    
    repo.save(tsr)
    return jsonify({'id': tsr.id, 'decision': tsr.go_no_go_decision.value})
```

### CI/CD Pipeline Integration

```yaml
# .github/workflows/ai-app-ci.yml
name: AI Application CI/CD

on:
  push:
    branches: [main]

jobs:
  test-and-evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run All Tests
        run: |
          pytest tests/unit --junitxml=results/unit.xml
          pytest tests/integration --junitxml=results/integration.xml
          pytest tests/evals --junitxml=results/evals.xml
          pytest tests/security --junitxml=results/security.xml
      
      - name: Generate TSR
        id: tsr
        run: |
          python scripts/generate_tsr.py \
            --results-dir results/ \
            --codebase-sha ${{ github.sha }}
          echo "tsr_id=$(cat tsr.json | jq -r '.id')" >> $GITHUB_OUTPUT
      
      - name: Upload TSR
        run: |
          curl -X POST $TSR_API_URL/api/tsr \
            -H "Content-Type: application/json" \
            -d @tsr.json
      
      - name: Check Go/No-Go
        run: |
          DECISION=$(curl -s $TSR_API_URL/api/tsr/${{ steps.tsr.outputs.tsr_id }}/go-no-go \
            | jq -r '.decision')
          if [ "$DECISION" = "no_go" ]; then
            echo "::error::Deployment blocked"
            exit 1
          fi
      
      - name: Deploy to Staging
        if: success()
        run: ./scripts/deploy-staging.sh
```

---

## Phase 10: Governance Viewer

### TSR Detail Page Sections

1. **Header** - TSR ID, date, decision status, environment
2. **Version Manifest** - Links to git commits for code, tests, prompts
3. **Test Results Breakdown** - Expandable results by test type
4. **AI Eval Iteration Timeline** - Visual V1→V2→V3 with metrics
5. **Failure Mode Registry** - All discovered issues with resolution status
6. **Requirement Coverage Matrix** - Requirements vs tests
7. **Compliance Checklist** - Auto-evaluated against rules
8. **Approval History** - Who approved, when, notes

### Governance Dashboard Template

```html
<!-- viewer/templates/governance/dashboard.html -->
<div class="governance-portal">
  <header class="gov-header">
    <span class="gov-header__icon">🏛️</span>
    <h1>AI Governance & Compliance Portal</h1>
  </header>
  
  <div class="gov-filters">
    <select id="filter-environment">
      <option value="">All Environments</option>
      <option value="production">Production</option>
      <option value="staging">Staging</option>
    </select>
    <select id="filter-decision">
      <option value="">All Decisions</option>
      <option value="go">Go</option>
      <option value="no_go">No-Go</option>
    </select>
  </div>
  
  <div class="tsr-list">
    {% for tsr in tsrs %}
    <div class="tsr-card tsr-card--{{ tsr.go_no_go_decision }}">
      <div class="tsr-card__header">
        <span class="tsr-card__id">{{ tsr.id[:12] }}</span>
        <span class="tsr-card__decision">
          {% if tsr.go_no_go_decision == 'go' %}✅ GO
          {% else %}❌ NO-GO{% endif %}
        </span>
      </div>
      <div class="tsr-card__versions">
        Code: <code>{{ tsr.versions.codebase_sha[:7] }}</code>
        Prompts: <code>{{ tsr.versions.prompts_version }}</code>
      </div>
      <a href="/governance/tsr/{{ tsr.id }}">View Details →</a>
    </div>
    {% endfor %}
  </div>
</div>
```

### Compliance Checklist

```html
<div class="compliance-checklist">
  <div class="compliance-item compliance-item--{{ 'pass' if unit_pass else 'fail' }}">
    <span class="compliance-item__check">{{ '☑' if unit_pass else '☐' }}</span>
    <span>All unit tests passing</span>
  </div>
  <div class="compliance-item compliance-item--{{ 'pass' if security_pass else 'fail' }}">
    <span class="compliance-item__check">{{ '☑' if security_pass else '☐' }}</span>
    <span>All security tests passing</span>
  </div>
  <div class="compliance-item compliance-item--{{ 'pass' if eval_accuracy else 'fail' }}">
    <span class="compliance-item__check">{{ '☑' if eval_accuracy else '☐' }}</span>
    <span>AI evaluation accuracy ≥ 85%</span>
  </div>
  <div class="compliance-item compliance-item--{{ 'pass' if no_critical else 'fail' }}">
    <span class="compliance-item__check">{{ '☑' if no_critical else '☐' }}</span>
    <span>All critical failure modes resolved</span>
  </div>
  <div class="compliance-item compliance-item--{{ 'pass' if coverage else 'fail' }}">
    <span class="compliance-item__check">{{ '☑' if coverage else '☐' }}</span>
    <span>Requirements coverage ≥ 95%</span>
  </div>
  
  <div class="compliance-status compliance-status--{{ 'compliant' if all_pass else 'non-compliant' }}">
    {{ 'COMPLIANT' if all_pass else 'NON-COMPLIANT' }}
  </div>
</div>
```

---

## Phase 11: Production Monitoring

### Monitoring Dashboard Components

| Component | Data Source | Update Frequency |
|-----------|-------------|------------------|
| Trace Volume Chart | Aggregated counts | 1 minute |
| Error Rate Chart | Failed trace % | 1 minute |
| Latency Percentiles | P50/P95/P99 | 1 minute |
| Live Trace Feed | WebSocket stream | Real-time |
| Anomaly Alerts | Anomaly detector | On detection |
| Satisfaction Score | User feedback | 5 minutes |
| Category Breakdown | Classified questions | 5 minutes |

### Production Trace Model

```python
# monitoring/models.py
@dataclass
class ProductionTrace:
    """A single AI interaction trace from production"""
    id: str
    timestamp: datetime
    question: str
    response: str
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    model_version: str
    prompt_version: str
    sources: List[dict] = field(default_factory=list)
    user_feedback: Optional[str] = None  # "positive", "negative"
    detected_category: Optional[str] = None
    anomaly_flags: List[str] = field(default_factory=list)
```

### Anomaly Detection

```python
# monitoring/anomaly.py
@dataclass
class AnomalyThresholds:
    latency_p95_multiplier: float = 1.5
    error_rate_threshold: float = 0.05
    satisfaction_drop_threshold: float = 0.10
    grounding_score_min: float = 0.85
    window_minutes: int = 15

class AnomalyDetector:
    def __init__(self, thresholds: AnomalyThresholds = None):
        self.thresholds = thresholds or AnomalyThresholds()
        self.baseline_latency_p95 = None
        self.baseline_satisfaction = None
    
    def set_baseline(self, latency_p95: float, satisfaction: float):
        self.baseline_latency_p95 = latency_p95
        self.baseline_satisfaction = satisfaction
    
    def check_latency_anomaly(self, current_p95: float) -> Optional[str]:
        if self.baseline_latency_p95:
            threshold = self.baseline_latency_p95 * self.thresholds.latency_p95_multiplier
            if current_p95 > threshold:
                return f"P95 latency ({current_p95}ms) exceeds threshold ({threshold}ms)"
        return None
```

### Drift Detection

```python
# monitoring/drift.py
def compare_to_baseline(production_metrics: dict, eval_baseline: dict) -> dict:
    """Compare production behavior to eval baseline"""
    results = {}
    
    for metric in ['accuracy', 'grounding_score', 'avg_response_length', 'latency_p95']:
        prod_value = production_metrics.get(metric)
        baseline_value = eval_baseline.get(metric)
        
        if prod_value and baseline_value:
            diff_pct = (prod_value - baseline_value) / baseline_value * 100
            status = 'ok' if abs(diff_pct) < 10 else 'warning' if abs(diff_pct) < 20 else 'critical'
            results[metric] = {
                'production': prod_value,
                'baseline': baseline_value,
                'diff_pct': diff_pct,
                'status': status
            }
    
    return results
```

### WebSocket Streaming

```python
# monitoring/stream.py
from flask_socketio import SocketIO, emit

socketio = None

def init_socketio(app):
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*")
    return socketio

def broadcast_trace(trace: dict):
    if socketio:
        socketio.emit('new_trace', trace, namespace='/monitoring')

def broadcast_alert(alert: dict):
    if socketio:
        socketio.emit('new_alert', alert, namespace='/monitoring')
```

### Live Traces JavaScript

```javascript
// viewer/static/js/live_traces.js
class LiveTraceViewer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.socket = io('/monitoring');
    this.traces = [];
    
    this.socket.on('new_trace', (trace) => this.addTrace(trace));
    this.socket.on('new_alert', (alert) => this.showAlert(alert));
  }
  
  addTrace(trace) {
    this.traces.unshift(trace);
    if (this.traces.length > 100) this.traces.pop();
    this.render();
  }
  
  render() {
    this.container.innerHTML = this.traces.map(t => `
      <div class="trace-item">
        <span class="trace-time">${this.formatTime(t.timestamp)}</span>
        <span class="trace-question">${t.question.substring(0, 50)}...</span>
        <span class="trace-latency">${t.latency_ms}ms</span>
        <span class="trace-feedback">${t.user_feedback === 'positive' ? '👍' : 
                                        t.user_feedback === 'negative' ? '👎' : '-'}</span>
      </div>
    `).join('');
  }
  
  showAlert(alert) {
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert--${alert.severity}`;
    alertEl.innerHTML = `⚠️ ${alert.description}`;
    document.getElementById('alerts').prepend(alertEl);
  }
}
```

---

## Implementation Order

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 6: Enhanced Code Viewer | 1 day | Phase 1 complete |
| Phase 7: TSR Models | 1 day | None |
| Phase 8: TSR Database & API | 1 day | Phase 7 |
| Phase 9: Governance Viewer | 1-2 days | Phase 8 |
| Phase 10: Production Monitoring | 1-2 days | Phase 7 |

Total: 5-7 days

---

## Acceptance Criteria

### Enhanced Code Viewer
- [ ] Line numbers displayed in gutter
- [ ] Click/shift-click line selection
- [ ] Keyboard navigation (j/k/y/g/Escape)
- [ ] Copy selected lines to clipboard
- [ ] Share link with line selection params
- [ ] URL params highlight lines on load

### Test Summary Report
- [ ] TSR generated from pytest JUnit XML
- [ ] Version manifest includes all SHAs
- [ ] Eval iteration history with metrics
- [ ] Failure modes with resolution status
- [ ] Automated go/no-go decision

### CI/CD Integration
- [ ] TSR stored in PostgreSQL
- [ ] API returns go/no-go decision
- [ ] Pipeline blocks on no-go (exit 1)
- [ ] Manual approval workflow

### Governance Viewer
- [ ] TSR list with filtering
- [ ] Detail view with all sections
- [ ] Version links to git commits
- [ ] Compliance checklist auto-evaluated
- [ ] PDF export

### Production Monitoring
- [ ] Real-time trace feed via WebSocket
- [ ] Anomaly alerts on threshold breach
- [ ] Satisfaction metrics aggregated
- [ ] Drift detection vs eval baseline

---

## Notes for Claude Code

- Use Flask-SocketIO for WebSocket support
- Use Chart.js for time series visualizations
- Use SQLAlchemy for database models
- PostgreSQL for TSR storage
- JUnit XML parsing with xml.etree
- PDF export with reportlab or weasyprint
- Line selection state in vanilla JS
- Keyboard shortcuts use vim conventions
- Governance portal uses formal color palette
- All timestamps in UTC, display in local timezone
