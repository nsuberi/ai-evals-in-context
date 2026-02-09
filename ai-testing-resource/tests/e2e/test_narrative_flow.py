"""
E2E Test: Narrative Flow

Tests the complete narrative educational journey through all phases.
"""


class TestNarrativeNavigation:
    """Test suite for narrative navigation flow"""

    def test_landing_page_loads(self, client):
        """GET / should return landing page with governance-first content"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Governance" in response.data or b"governance" in response.data

    def test_problem_page_loads(self, client):
        """GET /problem should return problem statement"""
        response = client.get("/problem")
        assert response.status_code == 200
        assert (
            b"churn" in response.data.lower()
            or b"support" in response.data.lower()
            or b"Problem" in response.data
        )

    def test_phase_pages_load(self, client):
        """Each phase page should load successfully"""
        for phase in range(1, 6):
            response = client.get(f"/phase/{phase}")
            assert response.status_code == 200, f"Phase {phase} failed to load"

    def test_governance_page_loads(self, client):
        """GET /governance should return governance overview"""
        response = client.get("/governance")
        assert response.status_code == 200

    def test_next_phase_links_present(self, client):
        """Each phase should have navigation links"""
        for phase in range(1, 5):  # Phases 1-4 should have "next"
            response = client.get(f"/phase/{phase}")
            assert b"phase-nav-btn" in response.data or b"Next" in response.data


class TestPhaseContent:
    """Test suite for phase-specific content"""

    def test_phase3_includes_test_type_cards(self, client):
        """Phase 3 should include test type card grid"""
        response = client.get("/phase/3")
        assert response.status_code == 200
        assert b"test-type-card" in response.data

    def test_phase3_ai_acceptance_card(self, client):
        """Phase 3 should have AI Acceptance test type card"""
        response = client.get("/phase/3")
        assert response.status_code == 200
        assert b"AI Acceptance" in response.data or b"ai_acceptance" in response.data

    def test_phase3_business_facing_badge(self, client):
        """Phase 3 should show Business-Facing badges on appropriate cards"""
        response = client.get("/phase/3")
        assert response.status_code == 200
        assert b"Business-Facing" in response.data

    def test_phase3_responsibility_note(self, client):
        """Phase 3 should show the test responsibility note"""
        response = client.get("/phase/3")
        assert response.status_code == 200
        assert b"test-responsibility-note" in response.data

    def test_phase3_no_code_section(self, client):
        """Phase 3 should not have code viewing section"""
        response = client.get("/phase/3")
        assert response.status_code == 200
        assert b"code-canvas" not in response.data
        assert b"show_code" not in response.data

    def test_phase4_includes_trace_content(self, client):
        """Phase 4 should include trace/evaluation content"""
        response = client.get("/phase/4")
        assert response.status_code == 200
        assert b"v1" in response.data.lower() or b"version" in response.data.lower()

    def test_phase4_accepts_version_param(self, client):
        """Phase 4 should accept version parameter"""
        response = client.get("/phase/4?version=v2")
        assert response.status_code == 200

    def test_phase4_failure_modes_v2(self, client):
        """Phase 4 v2 should show failure mode panel"""
        response = client.get("/phase/4?version=v2")
        assert response.status_code == 200
        assert b"failure-mode" in response.data

    def test_phase4_no_failure_modes_v3(self, client):
        """Phase 4 v3 should show panel with 'all evals pass' message"""
        response = client.get("/phase/4?version=v3")
        assert response.status_code == 200
        assert b"No failure modes" in response.data

    def test_phase4_architecture_context(self, client):
        """Phase 4 should include architecture context collapsible"""
        response = client.get("/phase/4?version=v1")
        assert response.status_code == 200
        assert b"Architecture Context" in response.data

    def test_phase5_includes_demo(self, client):
        """Phase 5 should include demo functionality"""
        response = client.get("/phase/5")
        assert response.status_code == 200
        assert b"question" in response.data.lower() or b"demo" in response.data.lower()

    def test_phase5_feedback_loop(self, client):
        """Phase 5 should have feedback loop back to Phase 1"""
        response = client.get("/phase/5")
        assert response.status_code == 200
        assert b"feedback-loop" in response.data


class TestLandingPageContent:
    """Test suite for landing page governance-first framing"""

    def test_landing_governance_framework(self, client):
        """Landing page should have three-part governance framework"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Governance" in response.data
        assert b"Approvals" in response.data
        assert b"Business Value" in response.data

    def test_landing_guiding_principle(self, client):
        """Landing page should have guiding principle quote"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"guiding-principle" in response.data

    def test_landing_rainbow_arc(self, client):
        """Landing page should have rainbow arc phase visual"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"rainbow-arc" in response.data

    def test_landing_phase_cards_updated(self, client):
        """Landing page phase cards should use new short titles"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Discovery" in response.data
        assert b"Design" in response.data
        assert b"Build" in response.data
        assert b"Iterate" in response.data
        assert b"Approve" in response.data
        assert b"Deploy" in response.data
        assert b"Monitor" in response.data

    def test_landing_tsr_preview(self, client):
        """Landing page should have TSR preview mock"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"tsr-preview" in response.data
        assert b"Test Summary Report" in response.data

    def test_landing_builder_bridge(self, client):
        """Landing page should have builder bridge section"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"builder-bridge" in response.data

    def test_landing_sdlc_title(self, client):
        """Landing page should label phases as 'The SDLC with AI'"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"SDLC with AI" in response.data


class TestGovernanceContent:
    """Test suite for governance tab content"""

    def test_governance_release_scoping(self, client):
        """Governance page should have release scoping callout"""
        response = client.get("/governance")
        assert response.status_code == 200
        assert (
            b"release-scoping-callout" in response.data
            or b"scoped to" in response.data.lower()
        )

    def test_governance_journey_complete(self, client):
        """Governance page should have Journey Complete section"""
        response = client.get("/governance")
        assert response.status_code == 200
        assert b"Journey Complete" in response.data


class TestBackwardCompatibility:
    """Ensure old routes still work"""

    def test_ask_still_works(self, client):
        """Legacy /ask route should still work"""
        response = client.get("/ask")
        assert response.status_code == 200

    def test_governance_dashboard_still_works(self, client):
        """Legacy /governance/dashboard route should still work"""
        response = client.get("/governance/dashboard")
        assert response.status_code == 200


class TestNavigationConsistency:
    """Test that navigation elements are consistent across pages"""

    def test_all_narrative_pages_have_phase_nav(self, client):
        """All narrative pages should have phase navigation"""
        routes = [
            "/",
            "/problem",
            "/phase/1",
            "/phase/2",
            "/phase/3",
            "/phase/4",
            "/phase/5",
            "/governance",
        ]
        for route in routes:
            response = client.get(route)
            assert response.status_code == 200
            assert (
                b"phase-nav" in response.data
            ), f"Route {route} missing phase navigation"

    def test_landing_has_start_cta(self, client):
        """Landing page should have Start Journey CTA"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Start" in response.data or b"Journey" in response.data


class TestPhase4API:
    """Test Phase 4 AJAX API endpoints"""

    def test_version_endpoint_v1(self, client):
        """GET /api/phase4/version/v1 should return version data"""
        response = client.get("/api/phase4/version/v1")
        assert response.status_code == 200
        data = response.get_json()
        assert data["version"] == "v1"
        assert "traces" in data
        assert "failure_modes" in data
        assert "arch_context" in data
        assert "axial_codes" in data
        assert "annotation_summary" in data

    def test_version_endpoint_v2(self, client):
        """GET /api/phase4/version/v2 should return version data"""
        response = client.get("/api/phase4/version/v2")
        assert response.status_code == 200
        data = response.get_json()
        assert data["version"] == "v2"
        assert len(data["failure_modes"]) > 0

    def test_version_endpoint_v3(self, client):
        """GET /api/phase4/version/v3 should return version data"""
        response = client.get("/api/phase4/version/v3")
        assert response.status_code == 200
        data = response.get_json()
        assert data["version"] == "v3"
        assert len(data["failure_modes"]) == 0

    def test_version_endpoint_invalid(self, client):
        """GET /api/phase4/version/v99 should return 400"""
        response = client.get("/api/phase4/version/v99")
        assert response.status_code == 400

    def test_axial_codes_endpoint(self, client):
        """GET /api/phase4/axial-codes should return code definitions"""
        response = client.get("/api/phase4/axial-codes")
        assert response.status_code == 200
        data = response.get_json()
        assert "axial_codes" in data
        assert "summary" in data
        assert "hallucination" in data["axial_codes"]
        assert "length_violation" in data["axial_codes"]

    def test_phase4_has_methodology_section(self, client):
        """Phase 4 should include qualitative coding methodology"""
        response = client.get("/phase/4")
        assert response.status_code == 200
        assert b"methodology-definitions" in response.data
        assert b"Qualitative Coding" in response.data

    def test_phase4_has_annotation_summary(self, client):
        """Phase 4 should include annotation summary table"""
        response = client.get("/phase/4")
        assert response.status_code == 200
        assert b"annotation-summary" in response.data

    def test_phase4_version_buttons(self, client):
        """Phase 4 should use buttons for version switching"""
        response = client.get("/phase/4")
        assert response.status_code == 200
        assert b'onclick="switchVersion' in response.data
