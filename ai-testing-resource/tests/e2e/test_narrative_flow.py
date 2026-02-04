"""
E2E Test: Narrative Flow

Tests the complete narrative educational journey through all phases.
"""
import pytest


class TestNarrativeNavigation:
    """Test suite for narrative navigation flow"""

    def test_landing_page_loads(self, client):
        """GET / should return landing page with journey content"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Acme Widget' in response.data or b'Journey' in response.data

    def test_problem_page_loads(self, client):
        """GET /problem should return problem statement"""
        response = client.get('/problem')
        assert response.status_code == 200
        # Should have business problem content
        assert b'churn' in response.data.lower() or b'support' in response.data.lower() or b'Problem' in response.data

    def test_phase_pages_load(self, client):
        """Each phase page should load successfully"""
        for phase in range(1, 6):
            response = client.get(f'/phase/{phase}')
            assert response.status_code == 200, f"Phase {phase} failed to load"

    def test_governance_page_loads(self, client):
        """GET /governance should return governance overview"""
        response = client.get('/governance')
        assert response.status_code == 200

    def test_next_phase_links_present(self, client):
        """Each phase should have navigation links"""
        for phase in range(1, 5):  # Phases 1-4 should have "next"
            response = client.get(f'/phase/{phase}')
            assert b'phase-nav-btn' in response.data or b'Next' in response.data


class TestPhaseContent:
    """Test suite for phase-specific content"""

    def test_phase3_includes_test_navigator(self, client):
        """Phase 3 should include Test Navigator content"""
        response = client.get('/phase/3')
        assert response.status_code == 200
        # Should have test type references
        assert b'unit' in response.data.lower() or b'test' in response.data.lower()

    def test_phase3_accepts_test_type_param(self, client):
        """Phase 3 should accept test_type parameter"""
        response = client.get('/phase/3?test_type=integration')
        assert response.status_code == 200

    def test_phase4_includes_trace_content(self, client):
        """Phase 4 should include trace/evaluation content"""
        response = client.get('/phase/4')
        assert response.status_code == 200
        # Should have version references
        assert b'v1' in response.data.lower() or b'version' in response.data.lower()

    def test_phase4_accepts_version_param(self, client):
        """Phase 4 should accept version parameter"""
        response = client.get('/phase/4?version=v2')
        assert response.status_code == 200

    def test_phase5_includes_demo(self, client):
        """Phase 5 should include demo functionality"""
        response = client.get('/phase/5')
        assert response.status_code == 200
        # Should have input form or demo reference
        assert b'question' in response.data.lower() or b'demo' in response.data.lower()


class TestBackwardCompatibility:
    """Ensure old routes still work"""

    def test_viewer_tests_still_works(self, client):
        """Legacy /viewer/tests route should still work"""
        response = client.get('/viewer/tests')
        assert response.status_code == 200

    def test_viewer_tests_with_type_still_works(self, client):
        """Legacy /viewer/tests/<type> route should still work"""
        response = client.get('/viewer/tests/unit')
        assert response.status_code == 200

    def test_viewer_traces_still_works(self, client):
        """Legacy /viewer/traces route should still work"""
        response = client.get('/viewer/traces')
        assert response.status_code == 200

    def test_viewer_traces_with_version_still_works(self, client):
        """Legacy /viewer/traces/<version> route should still work"""
        response = client.get('/viewer/traces/v1')
        assert response.status_code == 200

    def test_viewer_timeline_still_works(self, client):
        """Legacy /viewer/timeline route should still work"""
        response = client.get('/viewer/timeline')
        assert response.status_code == 200

    def test_ask_still_works(self, client):
        """Legacy /ask route should still work"""
        response = client.get('/ask')
        assert response.status_code == 200

    def test_governance_dashboard_still_works(self, client):
        """Legacy /governance/dashboard route should still work"""
        response = client.get('/governance/dashboard')
        assert response.status_code == 200


class TestNavigationConsistency:
    """Test that navigation elements are consistent across pages"""

    def test_all_narrative_pages_have_phase_nav(self, client):
        """All narrative pages should have phase navigation"""
        routes = ['/', '/problem', '/phase/1', '/phase/2', '/phase/3', '/phase/4', '/phase/5', '/governance']
        for route in routes:
            response = client.get(route)
            assert response.status_code == 200
            assert b'phase-nav' in response.data, f"Route {route} missing phase navigation"

    def test_landing_has_start_cta(self, client):
        """Landing page should have Start Journey CTA"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Start' in response.data or b'Journey' in response.data
