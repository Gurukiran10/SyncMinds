"""
Tests for action item CRUD endpoints.
"""
import pytest
from datetime import datetime, timedelta


def test_create_action_item(client, auth_headers, test_meeting, test_user):
    """POST /action-items/ creates an action item."""
    payload = {
        "title": "Write unit tests",
        "meeting_id": str(test_meeting.id),
        "owner_id": str(test_user.id),
        "priority": "high",
        "due_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
    }
    response = client.post("/api/v1/action-items/", json=payload, headers=auth_headers)
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["title"] == "Write unit tests"
    assert data["priority"] == "high"


def test_list_action_items(client, auth_headers, test_meeting, test_user, db):
    """GET /action-items/ returns items for the current user."""
    from app.models.action_item import ActionItem
    item = ActionItem(
        meeting_id=test_meeting.id,
        owner_id=test_user.id,
        title="Review PR",
        priority="medium",
        status="open",
    )
    db.add(item)
    db.commit()

    response = client.get("/api/v1/action-items/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(i["title"] == "Review PR" for i in data)


def test_update_action_item_status(client, auth_headers, test_meeting, test_user, db):
    """PUT/PATCH /action-items/{id} updates the status."""
    from app.models.action_item import ActionItem
    item = ActionItem(
        meeting_id=test_meeting.id,
        owner_id=test_user.id,
        title="Deploy to staging",
        priority="high",
        status="open",
    )
    db.add(item)
    db.commit()

    response = client.patch(
        f"/api/v1/action-items/{item.id}",
        json={"status": "completed"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_action_item_not_found(client, auth_headers):
    """GET/PATCH on unknown id returns 404."""
    import uuid
    response = client.patch(
        f"/api/v1/action-items/{uuid.uuid4()}",
        json={"status": "completed"},
        headers=auth_headers,
    )
    assert response.status_code == 404
