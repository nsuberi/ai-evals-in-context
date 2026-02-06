# Plan: Fix Static Asset (CSS/JS) Routing Through Proxy

## Problem Summary

Static assets (CSS, JS) are not loading when deployed behind CloudFront at `/ai-evals/`.

**Current behavior:**
- HTML contains: `href="/static/css/design-system.css"` (missing `/ai-evals` prefix)
- Correct path `/ai-evals/static/css/design-system.css` returns 200
- Generated path `/static/css/design-system.css` returns 403

**Root cause:** `APPLICATION_ROOT` is read from environment but only used for blueprint registration. Flask's config doesn't have it set, so `url_for('static', ...)` generates URLs without the prefix.

## Solution

Set Flask's `APPLICATION_ROOT` config value so `url_for()` generates correct static asset URLs.

## Implementation

### File: `ai-testing-resource/app/__init__.py`

Add this line after the app configuration section (around line 45):

```python
# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['TESTING'] = testing

# Set APPLICATION_ROOT for url_for() to generate correct static URLs
url_prefix = os.getenv('APPLICATION_ROOT', '') or None
if url_prefix:
    app.config['APPLICATION_ROOT'] = url_prefix
```

The key change is adding:
```python
if url_prefix:
    app.config['APPLICATION_ROOT'] = url_prefix
```

This tells Flask to prefix all generated URLs (including static assets) with `/ai-evals`.

## Expected Result After Fix

**Before (broken):**
```html
<link rel="stylesheet" href="/static/css/design-system.css">
```

**After (fixed):**
```html
<link rel="stylesheet" href="/ai-evals/static/css/design-system.css">
```

## Deploy and Verify

```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource

# Deploy
./scripts/deploy.sh

# Verify static URLs are correct
curl -s https://portfolio.cookinupideas.com/ai-evals/ | grep -E 'href.*\.css'
# Should show: href="/ai-evals/static/css/design-system.css"

# Verify CSS loads
curl -s -o /dev/null -w "%{http_code}" https://portfolio.cookinupideas.com/ai-evals/static/css/design-system.css
# Should return: 200

# Run steel thread tests
pytest tests/playwright/test_steel_thread.py -v --portfolio-url=https://portfolio.cookinupideas.com
```

## Critical Files

| Purpose | Path |
|---------|------|
| Flask App Init | `/ai-testing-resource/app/__init__.py` |
| Base Template | `/ai-testing-resource/templates/base.html` |
| Deploy Script | `/ai-testing-resource/scripts/deploy.sh` |
