"""
Webhook Endpoints
Handles inbound webhooks from Zoom, Google Calendar, Slack events.
"""
import hashlib
import hmac
import json
import logging
import os
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from fastapi import Depends

router = APIRouter()
logger = logging.getLogger(__name__)


# ── Zoom Webhooks ─────────────────────────────────────────────────────────────

def _verify_zoom_signature(payload: bytes, timestamp: str, signature: str) -> bool:
    """Verify Zoom webhook signature using HMAC-SHA256."""
    secret = settings.ZOOM_CLIENT_SECRET
    if not secret:
        logger.warning("ZOOM_CLIENT_SECRET not set — skipping signature verification")
        return True

    message = f"v0:{timestamp}:{payload.decode()}"
    expected = "v0=" + hmac.new(
        secret.encode(), message.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/zoom")
async def zoom_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_zm_request_timestamp: str = Header(default=""),
    x_zm_signature: str = Header(default=""),
):
    """
    Handle Zoom webhook events.
    Supported events:
    - endpoint.url_validation: Zoom's handshake challenge
    - recording.completed: triggers meeting processing pipeline
    """
    body = await request.body()

    # Verify signature
    if x_zm_signature and not _verify_zoom_signature(body, x_zm_request_timestamp, x_zm_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Zoom signature")

    try:
        payload: Dict[str, Any] = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    event = payload.get("event")

    # Zoom URL validation handshake
    if event == "endpoint.url_validation":
        plain_token = payload.get("payload", {}).get("plainToken", "")
        encrypted = hmac.new(
            settings.ZOOM_CLIENT_SECRET.encode() if settings.ZOOM_CLIENT_SECRET else b"",
            plain_token.encode(),
            hashlib.sha256,
        ).hexdigest()
        return {"plainToken": plain_token, "encryptedToken": encrypted}

    # Recording completed — kick off processing pipeline
    if event == "recording.completed":
        recording_payload = payload.get("payload", {})
        object_data = recording_payload.get("object", {})
        zoom_meeting_id = str(object_data.get("id", ""))
        recording_files = object_data.get("recording_files", [])

        # Find the audio/video recording URL
        recording_url = None
        for rf in recording_files:
            if rf.get("file_type") in ("MP4", "M4A", "audio_only"):
                recording_url = rf.get("download_url")
                break

        if not recording_url:
            logger.warning(f"Zoom recording.completed for {zoom_meeting_id}: no downloadable file found")
            return {"status": "no_recording_file"}

        # Find the matching Meeting record by external_id
        from app.models.meeting import Meeting
        meeting = db.execute(
            select(Meeting).where(
                Meeting.external_id == zoom_meeting_id,
                Meeting.platform == "zoom",
            )
        ).scalar_one_or_none()

        if not meeting:
            logger.warning(f"No Meeting found for Zoom meeting ID {zoom_meeting_id}")
            return {"status": "meeting_not_found"}

        # Download recording and enqueue processing
        background_tasks.add_task(
            _download_and_process_zoom_recording,
            str(meeting.id),
            recording_url,
            zoom_meeting_id,
        )
        logger.info(f"Enqueued processing for Zoom meeting {zoom_meeting_id} → Meeting {meeting.id}")
        return {"status": "processing_enqueued", "meeting_id": str(meeting.id)}

    logger.debug(f"Unhandled Zoom event: {event}")
    return {"status": "ignored", "event": event}


async def _download_and_process_zoom_recording(
    meeting_id: str,
    recording_url: str,
    zoom_meeting_id: str,
):
    """Download Zoom recording then kick off the Celery processing task."""
    import httpx
    from app.tasks.meeting_processor import process_meeting_recording_background

    os.makedirs("uploads/recordings", exist_ok=True)
    file_path = f"uploads/recordings/zoom_{zoom_meeting_id}.mp4"

    try:
        async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
            # Zoom requires auth token for download
            params = {}
            if settings.ZOOM_BOT_JWT:
                params["access_token"] = settings.ZOOM_BOT_JWT

            async with client.stream("GET", recording_url, params=params) as resp:
                resp.raise_for_status()
                with open(file_path, "wb") as f:
                    async for chunk in resp.aiter_bytes(chunk_size=8192):
                        f.write(chunk)

        logger.info(f"Downloaded Zoom recording to {file_path}")
        process_meeting_recording_background(meeting_id, file_path)
    except Exception as e:
        logger.error(f"Failed to download/process Zoom recording for meeting {meeting_id}: {e}")


# ── Google Calendar Webhooks ───────────────────────────────────────────────────

@router.post("/google/calendar")
async def google_calendar_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_goog_channel_id: str = Header(default=""),
    x_goog_resource_state: str = Header(default=""),
):
    """
    Handle Google Calendar push notifications.
    Triggers a calendar sync for the user associated with the channel.
    """
    if x_goog_resource_state == "sync":
        # Initial handshake — just acknowledge
        return {"status": "acknowledged"}

    if x_goog_resource_state in ("exists", "not_exists"):
        # A calendar event changed — extract user_id from channel_id (format: "user_{user_id}")
        user_id = None
        if x_goog_channel_id.startswith("user_"):
            user_id = x_goog_channel_id[5:]

        if user_id:
            background_tasks.add_task(_sync_google_calendar_for_user, user_id)
            logger.info(f"Google Calendar change detected for user {user_id} — sync enqueued")

    return {"status": "ok"}


async def _sync_google_calendar_for_user(user_id: str):
    """Sync Google Calendar for a single user."""
    from sqlalchemy.orm import Session
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.services.integrations.google_calendar import sync_user_calendar

    with SessionLocal() as db:
        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if user:
            await sync_user_calendar(db, user)
