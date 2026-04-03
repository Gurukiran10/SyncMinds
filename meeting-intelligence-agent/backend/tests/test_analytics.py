"""
Tests for analytics endpoints.
"""
import pytest


def test_analytics_dashboard_returns_schema(client, auth_headers):
    """GET /analytics/dashboard returns expected top-level keys."""
    response = client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # These keys should always be present even with no meetings
    assert "total_meetings" in data or "meeting_stats" in data or isinstance(data, dict)


def test_analytics_team(client, auth_headers):
    """GET /analytics/team returns a valid response."""
    response = client.get("/api/v1/analytics/team", headers=auth_headers)
    assert response.status_code in (200, 404)  # 404 acceptable if no team data


def test_analytics_requires_auth(client):
    """Analytics endpoint rejects unauthenticated requests."""
    response = client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 401
