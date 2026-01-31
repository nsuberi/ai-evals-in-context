"""
Acceptance Test: User Ask

Tests that users can ask questions and receive helpful responses.
These verify the core user requirements are met.
"""
import pytest


class TestUserAsk:
    """Test suite for user ask requirements"""

    def test_user_can_access_demo_page(self, client):
        """User should be able to access the demo page"""
        response = client.get('/ask')

        assert response.status_code == 200
        # Page should have form elements
        assert b'question' in response.data
        assert b'version' in response.data

    def test_user_can_select_version(self, client):
        """User should be able to select different versions"""
        response = client.get('/ask')

        assert b'v1' in response.data or b'V1' in response.data
        assert b'v2' in response.data or b'V2' in response.data
        assert b'v3' in response.data or b'V3' in response.data

    def test_demo_page_explains_versions(self, client):
        """Demo page should explain what each version does"""
        response = client.get('/ask')

        # Should have explanations
        assert b'Verbose' in response.data or b'verbose' in response.data
        assert b'RAG' in response.data or b'accurate' in response.data

    def test_form_has_submit_button(self, client):
        """Demo page should have a submit button"""
        response = client.get('/ask')

        assert b'Ask' in response.data or b'Submit' in response.data
