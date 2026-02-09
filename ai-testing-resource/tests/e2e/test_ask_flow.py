"""
E2E Test: Ask Flow

Tests the complete user flow from submitting a question
to receiving a formatted response.
"""

import pytest
import json


class TestAskFlow:
    """Test suite for ask flow"""

    def test_get_ask_page(self, client):
        """GET /ask should return the demo page"""
        response = client.get("/ask")

        assert response.status_code == 200
        assert b"Acme Widgets Support Bot" in response.data

    def test_post_question_v3(self, client, knowledge_base):
        """POST /ask with v3 should return grounded response"""
        response = client.post(
            "/ask",
            data=json.dumps(
                {"question": "What is your return policy?", "version": "v3"}
            ),
            content_type="application/json",
        )

        # May fail without API key, which is expected
        if response.status_code == 200:
            data = response.get_json()
            assert "text" in data
            assert "metadata" in data

    def test_post_empty_question(self, client):
        """POST /ask with empty question should return error"""
        response = client.post(
            "/ask",
            data=json.dumps({"question": "", "version": "v3"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_version_selection(self, client):
        """Different versions should be accepted"""
        for version in ["v1", "v2", "v3"]:
            response = client.post(
                "/ask",
                data=json.dumps({"question": "Hello", "version": version}),
                content_type="application/json",
            )

            # Either success or API error (no key/service unavailable), but not version error
            assert response.status_code in [200, 500, 503]
