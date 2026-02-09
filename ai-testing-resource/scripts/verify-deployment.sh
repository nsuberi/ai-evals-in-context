#!/bin/bash
set -e

PORTFOLIO_URL="${PORTFOLIO_URL:-https://portfolio.cookinupideas.com}"
APP_URL="${APP_URL:-https://portfolio.cookinupideas.com/ai-evals}"

echo "=== Verifying Deployment ==="

# Check health endpoint
echo "Checking health endpoint..."
HEALTH=$(curl -s "$APP_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "Health check: PASS"
else
    echo "Health check: FAIL"
    echo "Response: $HEALTH"
    exit 1
fi

# Check root page (should not return 500)
echo "Checking root page..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/")
if [ "$STATUS" == "200" ]; then
    echo "Root page: PASS (HTTP $STATUS)"
else
    echo "Root page: FAIL (HTTP $STATUS)"
    exit 1
fi

# Check ask page
echo "Checking /ask page..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/ask")
if [ "$STATUS" == "200" ]; then
    echo "Ask page: PASS (HTTP $STATUS)"
else
    echo "Ask page: FAIL (HTTP $STATUS)"
    exit 1
fi

# Check governance page
echo "Checking /governance..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/governance")
if [ "$STATUS" == "200" ]; then
    echo "Governance page: PASS (HTTP $STATUS)"
else
    echo "Governance page: FAIL (HTTP $STATUS)"
    exit 1
fi

echo ""
echo "=== All checks passed! ==="
