"""
Tests for meeting CRUD and agenda endpoints.
"""
import pytest
from datetime import datetime, timedelta


def test_create_meeting(client, auth_headers):
    """POST /meetings/ creates a meeting and returns it."""
    payload = {
        "title": "Sprint Planning",
        "platform": "manual",
        "scheduled_start": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "scheduled_end": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "attendee_ids": [],
    }
    response = client.post("/api/v1/meetings/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Sprint Planning"
    assert data["status"] == "scheduled"


def test_list_meetings(client, auth_headers, test_meeting):
    """GET /meetings/ returns a list of meetings for the current user."""
    response = client.get("/api/v1/meetings/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(m["title"] == "Test Meeting" for m in data)


def test_get_meeting_detail(client, auth_headers, test_meeting):
    """GET /meetings/{id} returns full meeting detail."""
    response = client.get(f"/api/v1/meetings/{test_meeting.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_meeting.id)
    assert "transcription_status" in data
    assert "analysis_status" in data


def test_get_meeting_not_found(client, auth_headers):
    """GET /meetings/{unknown_id} returns 404."""
    import uuid
    response = client.get(f"/api/v1/meetings/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_meeting(client, auth_headers, test_meeting):
    """DELETE /meetings/{id} soft-deletes a meeting."""
    response = client.delete(f"/api/v1/meetings/{test_meeting.id}", headers=auth_headers)
    assert response.status_code == 204


def test_get_agenda(client, auth_headers, test_meeting):
    """GET /meetings/{id}/agenda returns the agenda."""
    response = client.get(f"/api/v1/meetings/{test_meeting.id}/agenda", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "agenda" in data


def test_replace_agenda(client, auth_headers, test_meeting):
    """PUT /meetings/{id}/agenda replaces the agenda."""
    items = ["Define scope", "Review estimates", "Assign owners"]
    response = client.put(
        f"/api/v1/meetings/{test_meeting.id}/agenda",
        json=items,
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agenda"] == items


def test_add_agenda_item(client, auth_headers, test_meeting):
    """POST /meetings/{id}/agenda/items appends a new item."""
    item = {"text": "Discuss blockers", "time_box_minutes": 10}
    response = client.post(
        f"/api/v1/meetings/{test_meeting.id}/agenda/items",
        json=item,
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert any(
        (i.get("text") if isinstance(i, dict) else i) == "Discuss blockers"
        for i in data["agenda"]
    )


def test_remove_agenda_item(client, auth_headers, test_meeting, db):
    """DELETE /meetings/{id}/agenda/items/{index} removes an item."""
    # First set the agenda
    from app.models.meeting import Meeting
    from sqlalchemy import select
    meeting = db.execute(select(Meeting).where(Meeting.id == test_meeting.id)).scalar_one()
    meeting.agenda = ["Item 1", "Item 2", "Item 3"]
    db.commit()

    response = client.delete(
        f"/api/v1/meetings/{test_meeting.id}/agenda/items/1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["agenda"]) == 2
    assert data["removed"] == "Item 2"
