# Plan: Three Parallel Worktrees for Viewer Improvements

## Overview

Use git worktrees to work on three independent features in parallel:
1. **Fix Viewer Bugs** - Syntax highlighting not displaying, run code button returning XML error
2. **Add Steel Thread Test Type** - Add "Steel Thread" to Test Types sidebar
3. **Generate Real Traces** - Create 5+ real API traces per version (V1, V2, V3)

---

## Git Worktree Setup

```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource

# Create worktrees directory
mkdir -p ../worktrees

# Create three worktrees with feature branches
git worktree add ../worktrees/fix-viewer-bugs -b feature/fix-viewer-syntax-and-run-button
git worktree add ../worktrees/add-steelthread-tests -b feature/add-steelthread-test-type
git worktree add ../worktrees/generate-traces -b feature/generate-real-traces

# Verify
git worktree list
```

---

## Worktree 1: Fix Viewer Bugs

**Branch**: `feature/fix-viewer-syntax-and-run-button`
**Directory**: `../worktrees/fix-viewer-bugs`

### Problem 1: Syntax Highlighting Shows Grey on White

**Root Cause**: CSS selectors in `static/css/syntax-themes.css` use `.highlight .k` but the template doesn't wrap code in a `.highlight` class.

**Fix**: Add `highlight` class to `<pre>` elements in `templates/test_navigator.html`

```html
<!-- Line 56: Change from -->
<pre class="code-canvas__code"><code>{{ test_code | safe }}</code></pre>

<!-- To -->
<pre class="code-canvas__code highlight"><code>{{ test_code | safe }}</code></pre>

<!-- Line 73: Same change for app_code -->
<pre class="code-canvas__code highlight"><code>{{ app_code | safe }}</code></pre>
```

### Problem 2: Run Code Returns XML Parse Error

**Root Cause**: Likely 404 from proxy/routing issue returning XML error page instead of JSON.

**Investigation Steps**:
1. Check `static/js/viewer.js` line 34 - `appUrl()` function URL construction
2. Verify `APPLICATION_ROOT` handling in `templates/base.html` line 38
3. Test endpoint directly: `curl -X POST http://localhost:5000/viewer/tests/run/unit%2Ftest_sanitize`
4. Check Flask logs for route matching

**Files to Modify**:
- `templates/test_navigator.html` (lines 56, 73)
- Possibly `static/js/viewer.js` if URL construction is wrong

### Verification
```bash
flask run
# Visit http://localhost:5000/viewer/tests
# - Verify colored syntax (keywords red, strings blue)
# - Click "Run" button, confirm JSON response
```

---

## Worktree 2: Add Steel Thread Test Type

**Branch**: `feature/add-steelthread-test-type`
**Directory**: `../worktrees/add-steelthread-tests`

### Step 1: Add to TEST_TYPES

**File**: `viewer/test_navigator.py` (line 17)

```python
TEST_TYPES = [
    # ... existing entries ...
    {'id': 'performance', 'name': 'Performance', 'description': 'Test speed and efficiency'},
    {'id': 'steelthread', 'name': 'Steel Thread', 'description': 'End-to-end user journey tests'},  # ADD
]
```

### Step 2: Add to TestType Enum

**File**: `tsr/models.py` (line 25)

```python
class TestType(Enum):
    # ... existing entries ...
    PERFORMANCE = "performance"
    STEEL_THREAD = "steelthread"  # ADD
```

### Step 3: Create Test Directory

```bash
mkdir -p tests/steelthread
touch tests/steelthread/__init__.py
cp tests/playwright/test_steel_thread.py tests/steelthread/
cp tests/playwright/conftest.py tests/steelthread/
```

### Step 4: Create Explanation (Optional)

**File**: `data/explanations/steelthread.md`

```markdown
# Steel Thread Tests

Steel thread tests verify complete end-to-end user journeys from entry point to completion.

## What They Test
- Portfolio site loads correctly
- Navigation to deployed application works
- Core features are accessible and functional
- Error handling is graceful (no stack traces exposed)

## Why They Matter
Steel thread tests validate that all components work together in production, catching integration issues that unit tests miss.
```

### Verification
```bash
flask run
# Visit http://localhost:5000/viewer/tests
# - Verify "Steel Thread" appears in sidebar
# - Click it, verify tests are listed
pytest tests/steelthread/ -v
```

---

## Worktree 3: Generate Real Traces

**Branch**: `feature/generate-real-traces`
**Directory**: `../worktrees/generate-traces`

### Step 1: Create Generation Script

**File**: `scripts/generate_traces.py`

```python
#!/usr/bin/env python3
"""Generate real traces by calling the AI service."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ai_service import ask_v1, ask_v2, ask_v3, V1_SYSTEM_PROMPT, V2_SYSTEM_PROMPT, V3_SYSTEM_PROMPT

QUESTIONS = [
    "What is your return policy?",
    "How much does the Enterprise plan cost?",
    "What are the specs of Widget Pro X2?",
    "What shipping options do you offer?",
    "Do you offer a free trial?",
]

def generate_trace(version_func, version, question, index):
    result = version_func(question)
    return {
        "id": f"{version}-trace-{index:03d}",
        "version": version,
        "question": question,
        "prompt": {"v1": V1_SYSTEM_PROMPT, "v2": V2_SYSTEM_PROMPT, "v3": V3_SYSTEM_PROMPT[:200]}[version],
        "response": result["text"],
        "latency_ms": result["metadata"]["latency_ms"],
        "tokens": {
            "prompt": result["metadata"]["prompt_tokens"],
            "completion": result["metadata"]["completion_tokens"]
        },
        "sources": result.get("sources", []),
        "annotations": []
    }

def main():
    output_dir = Path("data/traces")

    for version, func in [("v1", ask_v1), ("v2", ask_v2), ("v3", ask_v3)]:
        print(f"Generating {version} traces...")
        traces = [generate_trace(func, version, q, i+1) for i, q in enumerate(QUESTIONS)]

        # Add version-specific annotations
        for t in traces:
            if version == "v1":
                wc = len(t["response"].split())
                t["annotations"].append({"type": "length_violation", "severity": "warning",
                    "text": f"Response is {wc} words", "span_start": None, "span_end": None})
            elif version == "v2":
                t["annotations"].append({"type": "missing_source", "severity": "warning",
                    "text": "No sources cited", "span_start": None, "span_end": None})
            elif version == "v3" and t["sources"]:
                t["annotations"].append({"type": "correct_retrieval", "severity": "success",
                    "text": f"Retrieved: {t['sources'][0]['title']}", "span_start": None, "span_end": None})

        with open(output_dir / f"{version}_traces.json", "w") as f:
            json.dump(traces, f, indent=2)
        print(f"  Saved {len(traces)} traces")

if __name__ == "__main__":
    main()
```

### Step 2: Run Script

```bash
export ANTHROPIC_API_KEY=your-key
python scripts/generate_traces.py
```

### Verification
```bash
flask run
# Visit http://localhost:5000/viewer/traces/v1
# - Verify 5+ traces listed
# - Click each, verify response and annotations display
# Repeat for /traces/v2 and /traces/v3
```

---

## Critical Files Summary

| Worktree | Files to Modify |
|----------|-----------------|
| fix-viewer-bugs | `templates/test_navigator.html`, possibly `static/js/viewer.js` |
| add-steelthread-tests | `viewer/test_navigator.py`, `tsr/models.py`, `tests/steelthread/` (new), `data/explanations/steelthread.md` (new) |
| generate-traces | `scripts/generate_traces.py` (new), `data/traces/v{1,2,3}_traces.json` |

---

## Merge Strategy

After completing all three:

```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource
git checkout main

# Merge each (or create PRs)
git merge feature/fix-viewer-syntax-and-run-button --no-ff
git merge feature/add-steelthread-test-type --no-ff
git merge feature/generate-real-traces --no-ff

# Cleanup
git worktree remove ../worktrees/fix-viewer-bugs
git worktree remove ../worktrees/add-steelthread-tests
git worktree remove ../worktrees/generate-traces
```

---

## End-to-End Verification

After merging all branches:

1. **Test Navigator**: Visit `/viewer/tests` - syntax highlighting works, run button returns JSON
2. **Steel Thread**: "Steel Thread" appears in sidebar, tests are listed and runnable
3. **Trace Inspector**: Visit `/viewer/traces/v1`, `/v2`, `/v3` - each shows 5+ traces with annotations
