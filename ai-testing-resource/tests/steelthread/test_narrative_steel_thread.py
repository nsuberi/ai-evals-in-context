"""Steel thread tests for narrative flow user journey.

These tests verify the complete educational journey from landing page
through all phases to governance, both locally and when deployed.
"""

import re
import pytest
from playwright.sync_api import Page, expect


# Deployed app base URL
DEPLOYED_APP_URL = "https://portfolio.cookinupideas.com/ai-evals"


class TestNarrativeJourneyLocal:
    """Tests for narrative flow with local/configured base URL."""

    def test_landing_page_has_start_journey(self, page: Page, base_url: str):
        """Landing page should have 'Start Journey' or similar CTA."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Look for journey/start CTA
        cta = page.locator("a, button").filter(has_text=re.compile(r"start|journey|begin|problem", re.I))
        expect(cta.first).to_be_visible(timeout=10000)

    def test_linear_navigation_through_phases(self, page: Page, base_url: str):
        """User can navigate linearly from landing through phases."""
        # Start at landing
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Click to problem
        start_link = page.locator("a").filter(has_text=re.compile(r"start|journey|problem", re.I))
        if start_link.count() > 0:
            start_link.first.click()
            page.wait_for_load_state("networkidle")
            # Should be at problem or phase 1
            assert "/problem" in page.url or "/phase" in page.url

    def test_phase3_test_navigator_functional(self, page: Page, base_url: str):
        """Phase 3 Test Navigator should allow browsing tests."""
        page.goto(f"{base_url}/phase/3")
        page.wait_for_load_state("networkidle")

        # Should have test type sidebar or tabs
        test_types = page.locator("a, button").filter(has_text=re.compile(r"unit|integration|e2e", re.I))
        expect(test_types.first).to_be_visible(timeout=10000)

    def test_phase4_version_selection(self, page: Page, base_url: str):
        """Phase 4 should allow selecting v1/v2/v3 versions."""
        page.goto(f"{base_url}/phase/4")
        page.wait_for_load_state("networkidle")

        # Should have version selectors
        versions = page.locator("a, button, [data-version]").filter(has_text=re.compile(r"v[123]|version", re.I))
        expect(versions.first).to_be_visible(timeout=10000)

    def test_phase5_demo_functional(self, page: Page, base_url: str):
        """Phase 5 demo should have input form and submit."""
        page.goto(f"{base_url}/phase/5")
        page.wait_for_load_state("networkidle")

        # Should have input and submit
        text_input = page.locator("input[type='text'], textarea").first
        expect(text_input).to_be_visible(timeout=10000)

        submit = page.locator("button[type='submit'], button:has-text('Ask'), button:has-text('Submit')")
        expect(submit.first).to_be_visible(timeout=10000)


class TestDeployedNarrativeJourney:
    """Tests for deployed app narrative flow at portfolio.cookinupideas.com/ai-evals."""

    def test_deployed_landing_loads(self, page: Page):
        """Deployed landing page should load successfully."""
        page.goto(DEPLOYED_APP_URL)
        page.wait_for_load_state("networkidle")

        # Should not be error page
        expect(page.locator("body")).to_be_visible()
        content = page.content().lower()
        # Should have some content (not just error)
        assert len(content) > 500

    def test_deployed_problem_page(self, page: Page):
        """Deployed /problem page should load."""
        page.goto(f"{DEPLOYED_APP_URL}/problem")
        page.wait_for_load_state("networkidle")

        expect(page.locator("body")).to_be_visible()

    def test_deployed_all_phases_accessible(self, page: Page):
        """All phase pages should be accessible on deployed app."""
        for phase in range(1, 6):
            page.goto(f"{DEPLOYED_APP_URL}/phase/{phase}")
            page.wait_for_load_state("networkidle")

            expect(page.locator("body")).to_be_visible()
            # Should have some content
            assert len(page.content()) > 500, f"Phase {phase} appears empty"

    def test_deployed_governance_accessible(self, page: Page):
        """Governance overview should be accessible."""
        page.goto(f"{DEPLOYED_APP_URL}/governance")
        page.wait_for_load_state("networkidle")

        expect(page.locator("body")).to_be_visible()

    def test_deployed_backward_compatibility(self, page: Page):
        """Legacy routes should still work on deployed app."""
        legacy_routes = [
            "/viewer/tests",
            "/viewer/traces",
            "/viewer/timeline",
            "/ask",
            "/governance/dashboard"
        ]

        for route in legacy_routes:
            page.goto(f"{DEPLOYED_APP_URL}{route}")
            page.wait_for_load_state("networkidle")

            # Should not return error
            content = page.content()
            assert "404" not in content or "not found" not in content.lower(), \
                f"Legacy route {route} appears broken"


class TestNarrativeHealthChecks:
    """Health check tests for narrative journey."""

    def test_local_health_endpoint(self, page: Page, base_url: str):
        """Local health endpoint should work."""
        page.goto(f"{base_url}/health")
        page.wait_for_load_state("networkidle")

        content = page.content()
        assert "healthy" in content.lower()

    def test_deployed_health_endpoint(self, page: Page):
        """Deployed health endpoint should work."""
        page.goto(f"{DEPLOYED_APP_URL}/health")
        page.wait_for_load_state("networkidle")

        content = page.content()
        assert "healthy" in content.lower()
