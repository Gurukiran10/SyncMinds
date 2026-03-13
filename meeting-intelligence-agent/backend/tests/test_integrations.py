"""
Tests for integration connect/disconnect/test endpoints and capture policy.
"""
import pytest
from app.services.capture_policy import evaluate_meeting


# ── Capture policy unit tests (no HTTP needed) ────────────────────────────────

def test_capture_policy_record_all_by_default():
    """With smart_recording_enabled=False, all meetings are recorded."""
    result = evaluate_meeting({"title": "Any meeting", "attendee_count": 1}, policy=None)
    assert result["should_record"] is True


def test_capture_policy_min_team_size_blocks_small_meetings():
    policy = {
        "smart_recording_enabled": True,
        "min_team_size": 3,
    }
    result = evaluate_meeting({"title": "1:1", "attendee_count": 2}, policy=policy)
    assert result["should_record"] is False
    assert "2" in result["reason"]


def test_capture_policy_exclude_keyword_blocks():
    policy = {
        "smart_recording_enabled": True,
        "min_team_size": 1,
        "exclude_keywords": ["confidential", "hr"],
    }
    result = evaluate_meeting(
        {"title": "HR onboarding discussion", "attendee_count": 3, "description": ""},
        policy=policy,
    )
    assert result["should_record"] is False


def test_capture_policy_include_keyword_required():
    policy = {
        "smart_recording_enabled": True,
        "min_team_size": 1,
        "include_keywords": ["engineering", "sprint"],
    }
    result = evaluate_meeting(
        {"title": "Marketing sync", "attendee_count": 5, "description": ""},
        policy=policy,
    )
    assert result["should_record"] is False


def test_capture_policy_include_keyword_passes():
    policy = {
        "smart_recording_enabled": True,
        "min_team_size": 1,
        "include_keywords": ["sprint"],
    }
    result = evaluate_meeting(
        {"title": "Sprint planning session", "attendee_count": 5, "description": ""},
        policy=policy,
    )
    assert result["should_record"] is True


def test_capture_policy_excluded_platform():
    policy = {
        "smart_recording_enabled": True,
        "min_team_size": 1,
        "exclude_platforms": ["teams"],
    }
    result = evaluate_meeting(
        {"title": "Weekly sync", "platform": "teams", "attendee_count": 4},
        policy=policy,
    )
    assert result["should_record"] is False


# ── Integration endpoint smoke tests ─────────────────────────────────────────

def test_integrations_status_requires_auth(client):
    """GET /integrations/status rejects unauthenticated requests."""
    response = client.get("/api/v1/integrations/")
    assert response.status_code == 401


def test_slack_connect_requires_auth(client):
    """POST /integrations/slack/connect rejects unauthenticated requests."""
    response = client.post("/api/v1/integrations/slack/connect", json={})
    assert response.status_code == 401
