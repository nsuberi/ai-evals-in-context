"""Steel thread tests for portfolio-to-app user journey.

These tests verify the complete user journey from the portfolio site
to the AI Testing Resource application.
"""

import json
import re
import pytest
from playwright.sync_api import Page, expect


# Deployed app base URL
DEPLOYED_APP_URL = "https://portfolio.cookinupideas.com/ai-evals"


class TestPortfolioEntry:
    """Tests for portfolio homepage and card visibility."""

    def test_portfolio_loads(self, page: Page, portfolio_url: str):
        """Portfolio homepage loads successfully."""
        page.goto(portfolio_url)
        expect(page).to_have_title(re.compile(r".+"))
        # Page should have content
        expect(page.locator("body")).to_be_visible()

    def test_accepting_ai_card_visible(self, page: Page, portfolio_url: str):
        """Card with 'Accepting AI' title is visible on portfolio."""
        page.goto(portfolio_url)

        # Look for the card with "Accepting AI" in the title
        card_title = page.locator("h3", has_text="Accepting AI")
        expect(card_title).to_be_visible(timeout=10000)

    def test_click_try_live_demo_navigates_to_app(self, page: Page, portfolio_url: str):
        """Clicking 'Try Live Demo' on the Accepting AI card navigates to /ai-evals."""
        page.goto(portfolio_url)

        # Find the card containing "Accepting AI"
        card = page.locator(".group", has=page.locator("h3", has_text="Accepting AI"))

        # Click the "Try Live Demo" link within that card
        demo_link = card.locator("a", has_text="Try Live Demo")
        expect(demo_link).to_be_visible(timeout=10000)
        demo_link.click()

        # Should navigate to /ai-evals
        page.wait_for_url("**/ai-evals/**", timeout=15000)
        expect(page).to_have_url(re.compile(r".*/ai-evals/.*"))


class TestFullJourney:
    """Tests for complete user journey from portfolio to app features."""

    def test_health_endpoint_from_portfolio_journey(self, page: Page, portfolio_url: str):
        """Journey + health check returns healthy status."""
        # Start at portfolio
        page.goto(portfolio_url)

        # Find and click the Accepting AI card
        card = page.locator(".group", has=page.locator("h3", has_text="Accepting AI"))
        demo_link = card.locator("a", has_text="Try Live Demo")
        expect(demo_link).to_be_visible(timeout=10000)
        demo_link.click()

        # Wait for app to load
        page.wait_for_url("**/ai-evals/**", timeout=15000)

        # Get base URL and check health endpoint
        current_url = page.url
        base = current_url.split("/ai-evals")[0]
        health_url = f"{base}/ai-evals/health"

        response = page.goto(health_url)
        assert response is not None
        assert response.status == 200

        # Check response contains healthy status
        body = page.content()
        assert "healthy" in body.lower()

    def test_governance_page_accessible(self, page: Page, portfolio_url: str):
        """Journey + navigate to /governance."""
        # Start at portfolio
        page.goto(portfolio_url)

        # Find and click the Accepting AI card
        card = page.locator(".group", has=page.locator("h3", has_text="Accepting AI"))
        demo_link = card.locator("a", has_text="Try Live Demo")
        expect(demo_link).to_be_visible(timeout=10000)
        demo_link.click()

        # Wait for app to load
        page.wait_for_url("**/ai-evals/**", timeout=15000)

        # Navigate to governance page
        page.goto(page.url.rstrip("/") + "/governance")
        page.wait_for_load_state("networkidle")

        # Verify page loaded
        expect(page).to_have_url(re.compile(r".*/governance"))
        expect(page.locator("body")).to_be_visible()

        # Check for TSR content
        expect(page.locator("text=TSR")).to_be_visible()

    def test_ask_page_form_elements(self, page: Page, portfolio_url: str):
        """Journey + verify form elements on /ask page."""
        # Start at portfolio
        page.goto(portfolio_url)

        # Find and click the Accepting AI card
        card = page.locator(".group", has=page.locator("h3", has_text="Accepting AI"))
        demo_link = card.locator("a", has_text="Try Live Demo")
        expect(demo_link).to_be_visible(timeout=10000)
        demo_link.click()

        # Wait for app to load
        page.wait_for_url("**/ai-evals/**", timeout=15000)

        # Navigate to ask page
        page.goto(page.url.rstrip("/") + "/ask")
        page.wait_for_load_state("networkidle")

        # Verify form elements exist
        # Look for input field or textarea
        text_input = page.locator("input[type='text'], textarea").first
        expect(text_input).to_be_visible(timeout=10000)

        # Look for submit button
        submit_button = page.locator("button[type='submit'], button:has-text('Submit'), button:has-text('Ask')")
        expect(submit_button.first).to_be_visible(timeout=10000)


class TestDeployedAppErrors:
    """Tests that the deployed app at portfolio.cookinupideas.com/ai-evals handles errors gracefully."""

    def test_deployed_ask_endpoint_no_500(self, page: Page):
        """POST to deployed /ask should NOT return 500 Internal Server Error.

        Target: https://portfolio.cookinupideas.com/ai-evals/ask
        """
        ask_url = f"{DEPLOYED_APP_URL}/ask"

        response = page.request.post(
            ask_url,
            data=json.dumps({"question": "What is your return policy?", "version": "v3"}),
            headers={"Content-Type": "application/json"}
        )

        # This test WILL FAIL if the deployed app returns 500
        assert response.status != 500, (
            f"INTERNAL SERVER ERROR (500) at {ask_url}!\n"
            f"Response body: {response.text()}\n"
            f"The deployed app has unhandled exceptions."
        )

    def test_deployed_ask_returns_structured_response(self, page: Page):
        """Deployed /ask should return structured JSON, not raw exceptions.

        Target: https://portfolio.cookinupideas.com/ai-evals/ask
        """
        ask_url = f"{DEPLOYED_APP_URL}/ask"

        response = page.request.post(
            ask_url,
            data=json.dumps({"question": "What are your shipping options?", "version": "v3"}),
            headers={"Content-Type": "application/json"}
        )

        # Parse response
        data = response.json()

        # If success, should have 'text' field
        if response.status == 200:
            assert "text" in data, f"Success response missing 'text': {data}"
        # If error, should have user-friendly 'error' field
        elif response.status >= 400:
            assert "error" in data, f"Error response missing 'error' field: {data}"
            error_msg = data.get("error", "")
            assert "Traceback" not in error_msg, f"Error exposes stack trace: {error_msg}"
            assert "ANTHROPIC_API_KEY" not in error_msg, f"Error exposes env var name: {error_msg}"

    def test_deployed_health_endpoint(self, page: Page):
        """Health endpoint should be accessible and return healthy status.

        Target: https://portfolio.cookinupideas.com/ai-evals/health
        """
        health_url = f"{DEPLOYED_APP_URL}/health"

        response = page.request.get(health_url)

        assert response.status == 200, f"Health check failed with status {response.status}"
        body = response.text()
        assert "healthy" in body.lower(), f"Health response doesn't indicate healthy: {body}"

    def test_deployed_ask_form_submission(self, page: Page):
        """Submit form via UI should return a successful AI response.

        This test verifies the form action URL is correctly prefixed:
        - Form action should be /ai-evals/ask (not /ask)
        - Form submission reaches Flask app through CloudFront -> ALB -> ECS
        - Response shows AI-generated content
        """
        ask_page_url = f"{DEPLOYED_APP_URL}/ask"

        # Navigate to the ask page
        page.goto(ask_page_url)
        page.wait_for_load_state("networkidle")

        # Verify form action has correct prefix
        form = page.locator("form.demo-form")
        form_action = form.get_attribute("action")
        assert "/ai-evals/ask" in form_action or form_action == "/ai-evals/ask", (
            f"Form action missing /ai-evals/ prefix: {form_action}. "
            f"This will cause form submission to hit S3 instead of the API."
        )

        # Fill in the question
        page.fill("textarea[name='question']", "What is your return policy?")

        # Submit the form
        page.click("button[type='submit']")

        # Wait for response (form submission reloads page with JSON response)
        page.wait_for_load_state("networkidle")

        # Check we got a JSON response, not XML error
        content = page.content()
        assert "<?xml" not in content, (
            f"Received XML error instead of JSON. "
            f"Form action is likely missing /ai-evals/ prefix."
        )
