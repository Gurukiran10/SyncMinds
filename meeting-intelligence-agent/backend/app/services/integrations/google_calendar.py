"""
Google Calendar Integration Service
Syncs Google Calendar events into Meeting records.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.models.meeting import Meeting
from app.models.user import User

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _build_google_service(access_token: str, refresh_token: Optional[str] = None):
    """Build a Google Calendar API client from stored OAuth tokens."""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=SCOPES,
        )
        return build("calendar", "v3", credentials=creds, cache_discovery=False)
    except ImportError:
        logger.warning("google-api-python-client not installed — cannot sync calendar")
        return None
    except Exception as e:
        logger.error(f"Failed to build Google Calendar service: {e}")
        return None


def _parse_event_time(time_dict: Dict) -> Optional[datetime]:
    """Parse a Google Calendar event time dict into a datetime."""
    dt_str = time_dict.get("dateTime") or time_dict.get("date")
    if not dt_str:
        return None
    try:
        # dateTime: "2024-01-15T10:00:00+05:30"  |  date: "2024-01-15"
        if "T" in dt_str:
            dt = datetime.fromisoformat(dt_str)
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        else:
            return datetime.strptime(dt_str, "%Y-%m-%d")
    except ValueError:
        return None


def _extract_attendee_emails(event: Dict) -> List[str]:
    return [
        a["email"]
        for a in event.get("attendees", [])
        if a.get("email") and not a.get("resource")
    ]


async def sync_user_calendar(db: Session, user: User) -> int:
    """
    Sync Google Calendar events for the next 7 days into Meeting records.
    Returns the number of new meetings created.
    """
    integrations = user.integrations or {}
    google_creds = integrations.get("google", {})
    access_token = google_creds.get("access_token")
    refresh_token = google_creds.get("refresh_token")

    if not access_token:
        logger.debug(f"User {user.id} has no Google access token — skipping")
        return 0

    service = _build_google_service(access_token, refresh_token)
    if not service:
        return 0

    now = datetime.utcnow()
    time_min = now.isoformat() + "Z"
    time_max = (now + timedelta(days=7)).isoformat() + "Z"

    try:
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
                maxResults=50,
            )
            .execute()
        )
    except Exception as e:
        logger.error(f"Google Calendar API error for user {user.id}: {e}")
        return 0

    events = events_result.get("items", [])
    created = 0

    for event in events:
        event_id = event.get("id")
        if not event_id:
            continue

        # Skip events with no start time (all-day events without time are skipped)
        start = _parse_event_time(event.get("start", {}))
        end = _parse_event_time(event.get("end", {}))
        if not start:
            continue

        # Check if meeting already exists for this Google event
        existing = db.execute(
            select(Meeting).where(
                Meeting.external_id == event_id,
                Meeting.platform == "google",
            )
        ).scalar_one_or_none()

        if existing:
            # Update scheduled times if they changed
            if existing.scheduled_start != start:
                existing.scheduled_start = start  # type: ignore[assignment]
                existing.scheduled_end = end  # type: ignore[assignment]
                db.commit()
            continue

        # Build attendee list
        attendee_emails = _extract_attendee_emails(event)
        attendee_ids = []
        for email in attendee_emails:
            attendee_user = db.execute(
                select(User).where(User.email == email)
            ).scalar_one_or_none()
            if attendee_user:
                attendee_ids.append(str(attendee_user.id))

        # Determine meeting platform from conference data
        conference = event.get("conferenceData", {})
        entry_points = conference.get("entryPoints", [])
        join_url = next(
            (ep.get("uri") for ep in entry_points if ep.get("entryPointType") == "video"),
            None,
        )

        meeting = Meeting(
            title=event.get("summary") or "Untitled Meeting",
            description=event.get("description") or "",
            organizer_id=user.id,
            scheduled_start=start,
            scheduled_end=end,
            platform="google",
            external_id=event_id,
            join_url=join_url,
            attendee_ids=attendee_ids or [str(user.id)],
            status="scheduled",
            transcription_status="pending",
            analysis_status="pending",
            agenda=[],
            meeting_metadata={
                "google_event_id": event_id,
                "calendar_link": event.get("htmlLink"),
                "location": event.get("location"),
            },
        )
        db.add(meeting)
        created += 1

    if created:
        db.commit()
        logger.info(f"Created {created} new meetings from Google Calendar for user {user.id}")

    return created


async def get_upcoming_events(access_token: str, refresh_token: Optional[str] = None, days: int = 7) -> List[Dict]:
    """Return raw Google Calendar events for the next N days (used by API endpoints)."""
    service = _build_google_service(access_token, refresh_token)
    if not service:
        return []

    now = datetime.utcnow()
    try:
        result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now.isoformat() + "Z",
                timeMax=(now + timedelta(days=days)).isoformat() + "Z",
                singleEvents=True,
                orderBy="startTime",
                maxResults=20,
            )
            .execute()
        )
        return result.get("items", [])
    except Exception as e:
        logger.error(f"Failed to fetch Google Calendar events: {e}")
        return []
