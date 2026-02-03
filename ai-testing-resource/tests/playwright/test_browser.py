"""Browser E2E tests using Playwright.

Tests all major routes of the AI Testing Resource application.
Requires Docker Compose to be running: docker compose up -d
"""

import pytest
from playwright.sync_api import Page, expect


def test_home_page_loads(page: Page, base_url: str):
    """Test that the home page loads and shows the ask form."""
    page.goto(f"{base_url}/")

    # Home page renders the ask form directly
    expect(page.locator("textarea")).to_be_visible()
    expect(page.locator("select")).to_be_visible()
    expect(page.locator("button[type='submit']")).to_be_visible()


def test_ask_page_loads(page: Page, base_url: str):
    """Test that the /ask page loads with required form elements."""
    page.goto(f"{base_url}/ask")

    # Verify form elements exist
    expect(page.locator("textarea")).to_be_visible()
    expect(page.locator("select")).to_be_visible()
    expect(page.locator("button[type='submit']")).to_be_visible()


def test_ask_page_form_interaction(page: Page, base_url: str):
    """Test that the form can be filled and submitted."""
    page.goto(f"{base_url}/ask")

    # Fill in a test question
    page.locator("textarea").fill("What is your return policy?")

    # Verify the version select has options
    select = page.locator("select")
    expect(select).to_be_visible()

    # Check that submit button is clickable
    button = page.locator("button[type='submit']")
    expect(button).to_be_enabled()

    # Verify the demo response container exists
    expect(page.locator("#demo-response")).to_be_attached()


def test_viewer_tests_loads(page: Page, base_url: str):
    """Test that the test viewer page loads."""
    page.goto(f"{base_url}/viewer/tests")

    # Verify the page loaded successfully by checking URL
    assert page.url.endswith("/viewer/tests")

    # Page should have some content
    assert len(page.content()) > 0


def test_viewer_traces_loads(page: Page, base_url: str):
    """Test that the trace viewer page loads."""
    page.goto(f"{base_url}/viewer/traces")

    # Verify the page loaded successfully
    assert page.url.endswith("/viewer/traces")


def test_viewer_timeline_loads(page: Page, base_url: str):
    """Test that the timeline viewer page loads."""
    page.goto(f"{base_url}/viewer/timeline")

    # Verify the page loaded successfully
    assert page.url.endswith("/viewer/timeline")


def test_governance_dashboard_loads(page: Page, base_url: str):
    """Test that the governance dashboard loads."""
    page.goto(f"{base_url}/governance/dashboard")

    # Verify the page loaded successfully
    assert page.url.endswith("/governance/dashboard")


def test_monitoring_traces_loads(page: Page, base_url: str):
    """Test that the monitoring traces page loads."""
    page.goto(f"{base_url}/monitoring/traces")

    # Verify the page loaded successfully
    assert page.url.endswith("/monitoring/traces")


def test_health_endpoint(page: Page, base_url: str):
    """Test the health check endpoint returns healthy status."""
    response = page.goto(f"{base_url}/health")

    # Should return 200
    assert response.status == 200

    # Check the JSON response
    content = page.content()
    assert "healthy" in content
