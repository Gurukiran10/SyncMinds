"""
Background Tasks for Meeting Processing
"""
import logging
from datetime import datetime
from typing import List, Optional
from celery import shared_task
from app.core.database import SessionLocal
from app.services.ai.transcription import transcription_service
from app.services.ai.nlp import nlp_service
from app.services.integrations.slack import slack_service
from app.services.mentions import detect_and_store_mentions
from app.models.meeting import Meeting
from app.models.transcript import Transcript
from app.models.action_item import ActionItem
from app.models.user import User
from sqlalchemy import select

logger = logging.getLogger(__name__)


def _match_user_by_name(users: List[User], owner_name: Optional[str]) -> Optional[User]:
    if not owner_name:
        return None
    target = owner_name.strip().lower()
    if not target:
        return None
    for user in users:
        aliases = {
            str(user.full_name or "").strip().lower(),
            str(user.username or "").strip().lower(),
            str(user.email or "").split("@")[0].strip().lower(),
        }
        first_name = str(user.full_name or "").split()[0].strip().lower() if str(user.full_name or "").strip() else ""
        if first_name:
            aliases.add(first_name)
        if target in aliases:
            return user
    return None


def _parse_due_date(value: Optional[str]):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@shared_task(name="process_meeting_recording")
def process_meeting_recording(meeting_id: str, recording_path: str):
    """
    Process meeting recording:
    1. Transcribe audio with speaker diarization
    2. Extract action items, mentions, decisions
    3. Generate summary
    4. Send notifications
    """
    import asyncio
    asyncio.run(_process_meeting_async(meeting_id, recording_path))


def process_meeting_recording_background(meeting_id: str, recording_path: str):
    """FastAPI BackgroundTasks entrypoint for meeting processing"""
    import asyncio
    import threading

    def _runner() -> None:
        asyncio.run(_process_meeting_async(meeting_id, recording_path))

    threading.Thread(target=_runner, daemon=True).start()


async def _process_meeting_async(meeting_id: str, recording_path: str):  # type: ignore
    """Async implementation of meeting processing"""
    meeting = None
    with SessionLocal() as db:
        try:
            # Get meeting
            result = db.execute(
                select(Meeting).where(Meeting.id == meeting_id)
            )
            meeting = result.scalar_one_or_none()
            
            if not meeting:
                logger.error(f"Meeting {meeting_id} not found")
                return
            
            # Step 1: Transcribe
            logger.info(f"Transcribing meeting {meeting_id}")
            meeting.transcription_status = "processing"  # type: ignore
            db.commit()
            
            transcription = await transcription_service.transcribe_audio(
                recording_path,
                enable_diarization=True,
            )
            
            # Save transcripts
            for idx, segment in enumerate(transcription.segments):
                transcript = Transcript(
                    meeting_id=meeting.id,
                    segment_number=idx,
                    speaker_id=segment.speaker,
                    text=segment.text,
                    start_time=segment.start,
                    end_time=segment.end,
                    duration=segment.end - segment.start,
                    confidence=segment.confidence,
                )
                db.add(transcript)
            
            meeting.transcription_status = "completed"  # type: ignore
            db.commit()
            
            # Step 2: Analyze with NLP
            logger.info(f"Analyzing meeting {meeting_id}")
            meeting.analysis_status = "processing"  # type: ignore
            db.commit()
            
            full_transcript = "\n".join([s.text for s in transcription.segments])
            
            # Generate summary
            summary = await nlp_service.generate_summary(
                full_transcript,
                meeting.title,  # type: ignore[arg-type]
                meeting.attendee_ids or [],  # type: ignore[arg-type]
            )
            
            meeting.summary = summary.executive_summary  # type: ignore
            meeting.key_decisions = [d.dict() for d in summary.decisions]  # type: ignore
            meeting.discussion_topics = summary.discussion_topics  # type: ignore
            meeting.sentiment_score = summary.sentiment_score  # type: ignore

            # Compute meeting quality score
            try:
                from app.services.attendee_optimizer import compute_meeting_quality_score
                scheduled_start = meeting.scheduled_start
                scheduled_end = meeting.scheduled_end
                if scheduled_start and scheduled_end:
                    duration_minutes = (scheduled_end - scheduled_start).total_seconds() / 60
                else:
                    duration_minutes = 60
                meeting.meeting_quality_score = compute_meeting_quality_score(  # type: ignore
                    executive_summary=summary.executive_summary or "",
                    decisions=summary.decisions,
                    action_items=summary.action_items,
                    sentiment_score=summary.sentiment_score or 0.0,
                    duration_minutes=duration_minutes,
                    attendee_count=len(meeting.attendee_ids or []),
                )
            except Exception as qs_err:
                logger.warning(f"Quality score computation failed (non-fatal): {qs_err}")

            candidate_users = db.execute(select(User).where(User.is_active.is_(True))).scalars().all()
            
            # Save action items
            for action_data in summary.action_items:
                owner = _match_user_by_name(candidate_users, action_data.owner)
                action = ActionItem(
                    meeting_id=meeting.id,
                    owner_id=(owner.id if owner else meeting.organizer_id),
                    title=action_data.title,
                    description=action_data.description,
                    priority=action_data.priority,
                    due_date=_parse_due_date(action_data.due_date),
                    confidence_score=action_data.confidence,
                    extraction_method="ai_detected",
                    extracted_from_text=full_transcript[:500],
                    item_metadata={
                        "owner_name": action_data.owner,
                        "due_date_raw": action_data.due_date,
                    },
                )
                db.add(action)

            # Step 2.5: Save personalized mentions for present or absent users
            organizer = db.execute(
                select(User).where(User.id == meeting.organizer_id)
            ).scalar_one_or_none()

            await detect_and_store_mentions(
                db=db,
                meeting=meeting,
                transcript_text=full_transcript,
                candidate_users=candidate_users,
                send_real_time_alerts=True,
                meeting_context={
                    "meeting_summary": summary.executive_summary,
                    "discussion_topics": summary.discussion_topics,
                },
            )
            
            meeting.analysis_status = "completed"  # type: ignore
            meeting.status = "completed"  # type: ignore
            db.commit()

            # Step 2.6: Index meeting for semantic search
            try:
                from app.services.knowledge.embeddings import index_meeting
                index_meeting(db, meeting, full_transcript)
            except Exception as idx_err:
                logger.warning(f"Knowledge indexing failed (non-fatal): {idx_err}")

            # Step 3: Send Slack notification (if organizer has Slack connected)
            if organizer:
                slack_creds = (organizer.integrations or {}).get("slack", {})
                if slack_creds.get("bot_token"):
                    try:
                        logger.info(f"Sending Slack notification for meeting {meeting_id}")
                        await _notify_slack(
                            token=slack_creds["bot_token"],
                            channel=slack_creds.get("default_channel", "#general"),
                            meeting=meeting,
                            action_count=len(summary.action_items),
                            decision_count=len(summary.decisions),
                        )
                    except Exception as slack_err:
                        logger.warning(f"Slack notification failed (non-fatal): {slack_err}")
                elif organizer.email:
                    # Fallback: send summary via email when Slack is not connected
                    try:
                        from app.services.notifications.email import send_post_meeting_summary
                        from app.core.config import settings as _settings
                        await send_post_meeting_summary(
                            user_email=str(organizer.email),
                            meeting_title=str(meeting.title),
                            executive_summary=summary.executive_summary or "",
                            decisions=[d.dict() for d in summary.decisions],
                            action_items=[a.dict() for a in summary.action_items],
                            meeting_url=f"{_settings.APP_BASE_URL}/meetings/{meeting.id}",
                        )
                    except Exception as email_err:
                        logger.warning(f"Email notification failed (non-fatal): {email_err}")

            # Step 4: Create Linear issues for action items (if organizer has Linear connected)
            if organizer and summary.action_items:
                linear_creds = (organizer.integrations or {}).get("linear", {})
                if linear_creds.get("api_key"):
                    try:
                        logger.info(f"Creating Linear issues for meeting {meeting_id}")
                        await _create_linear_issues(
                            api_key=linear_creds["api_key"],
                            meeting_title=str(meeting.title),
                            action_items=summary.action_items,
                        )
                    except Exception as linear_err:
                        logger.warning(f"Linear sync failed (non-fatal): {linear_err}")

            # Step 5: Create Jira issues for action items (if organizer has Jira connected)
            if organizer and summary.action_items:
                jira_creds = (organizer.integrations or {}).get("jira", {})
                if jira_creds.get("api_token") and jira_creds.get("default_project"):
                    try:
                        logger.info(f"Creating Jira issues for meeting {meeting_id}")
                        await _create_jira_issues(
                            jira_url=jira_creds.get("url", ""),
                            username=jira_creds.get("username", ""),
                            api_token=jira_creds["api_token"],
                            project_key=jira_creds["default_project"],
                            meeting_title=str(meeting.title),
                            action_items=summary.action_items,
                        )
                    except Exception as jira_err:
                        logger.warning(f"Jira sync failed (non-fatal): {jira_err}")

            # Step 6: Create Asana tasks for action items (if organizer has Asana connected)
            if organizer and summary.action_items:
                asana_creds = (organizer.integrations or {}).get("asana", {})
                if asana_creds.get("access_token") and asana_creds.get("workspace_gid"):
                    try:
                        logger.info(f"Creating Asana tasks for meeting {meeting_id}")
                        await _create_asana_tasks(
                            access_token=asana_creds["access_token"],
                            workspace_gid=asana_creds["workspace_gid"],
                            project_gid=asana_creds.get("default_project_gid"),
                            meeting_title=str(meeting.title),
                            action_items=summary.action_items,
                        )
                    except Exception as asana_err:
                        logger.warning(f"Asana sync failed (non-fatal): {asana_err}")

            logger.info(f"Meeting {meeting_id} processing completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing meeting {meeting_id}: {e}", exc_info=True)
            if meeting:
                try:
                    db.rollback()
                except Exception:
                    pass
                try:
                    result = db.execute(select(Meeting).where(Meeting.id == meeting_id))
                    failed_meeting = result.scalar_one_or_none()
                    if failed_meeting:
                        failed_meeting.transcription_status = "failed"  # type: ignore
                        failed_meeting.analysis_status = "failed"  # type: ignore
                        failed_meeting.status = "failed"  # type: ignore
                        db.commit()
                except Exception as status_error:
                    logger.error(
                        f"Failed to persist failed status for meeting {meeting_id}: {status_error}",
                        exc_info=True,
                    )


@shared_task(name="send_action_reminders")
def send_action_reminders():
    """Send reminders for upcoming action items"""
    import asyncio
    asyncio.run(_send_reminders_async())


async def _send_reminders_async():
    """Send action item reminders"""
    with SessionLocal() as db:
        from datetime import datetime, timedelta
        
        tomorrow = datetime.utcnow() + timedelta(days=1)
        
        # Get action items due tomorrow
        result = db.execute(
            select(ActionItem).where(
                ActionItem.status == "open",
                ActionItem.due_date >= datetime.utcnow(),
                ActionItem.due_date <= tomorrow,
                ActionItem.reminder_sent_24h == False,
            )
        )
        
        items = result.scalars().all()
        
        for item in items:
            try:
                await slack_service.send_action_reminder(
                    user_id=str(item.owner_id),
                    action_item={
                        "id": str(item.id),
                        "title": item.title,
                        "description": item.description,
                        "due_date": item.due_date.strftime("%Y-%m-%d"),
                        "priority": item.priority,
                    },
                )
                item.reminder_sent_24h = True  # type: ignore
                item.reminder_count += 1  # type: ignore
            except Exception as e:
                logger.error(f"Failed to send reminder for action {item.id}: {e}")
        
        db.commit()
        logger.info(f"Sent {len(items)} action item reminders")


@shared_task(name="dispatch_pre_meeting_briefs")
def dispatch_pre_meeting_briefs():
    """Scan for meetings starting in ~30 minutes and send pre-meeting briefs."""
    import asyncio
    asyncio.run(_dispatch_briefs_async())


async def _dispatch_briefs_async():
    from datetime import datetime, timedelta
    from app.models.user import User
    from app.services.pre_meeting_briefs import PreMeetingBriefService

    brief_service = PreMeetingBriefService()
    now = datetime.utcnow()
    window_start = now + timedelta(minutes=25)
    window_end = now + timedelta(minutes=35)

    with SessionLocal() as db:
        result = db.execute(
            select(Meeting).where(
                Meeting.scheduled_start >= window_start,
                Meeting.scheduled_start <= window_end,
                Meeting.status == "scheduled",
            )
        )
        meetings = result.scalars().all()
        logger.info(f"Dispatching pre-meeting briefs for {len(meetings)} meetings")

        for meeting in meetings:
            attendee_ids = meeting.attendee_ids or []
            for uid in attendee_ids:
                user = db.execute(select(User).where(User.id == uid)).scalar_one_or_none()
                if user and user.is_active:
                    try:
                        await brief_service.generate_brief_for_user(db, meeting, user)
                    except Exception as e:
                        logger.error(f"Brief failed for user {uid} / meeting {meeting.id}: {e}")


@shared_task(name="escalate_overdue_action_items")
def escalate_overdue_action_items():
    """Escalate action items that are overdue and haven't been escalated yet."""
    import asyncio
    asyncio.run(_escalate_overdue_async())


async def _escalate_overdue_async():
    from datetime import datetime

    with SessionLocal() as db:
        result = db.execute(
            select(ActionItem).where(
                ActionItem.status == "open",
                ActionItem.due_date < datetime.utcnow(),
                ActionItem.reminder_sent_overdue.is_(False),  # type: ignore[attr-defined]
            )
        )
        items = result.scalars().all()
        logger.info(f"Escalating {len(items)} overdue action items")

        for item in items:
            try:
                await slack_service.send_action_reminder(
                    user_id=str(item.owner_id),
                    action_item={
                        "id": str(item.id),
                        "title": item.title,
                        "description": item.description,
                        "due_date": item.due_date.strftime("%Y-%m-%d") if item.due_date else "no date",
                        "priority": item.priority,
                        "overdue": True,
                    },
                )
                item.reminder_sent_overdue = True  # type: ignore[attr-defined]
                item.reminder_count += 1  # type: ignore[attr-defined]
            except Exception as e:
                logger.error(f"Failed to escalate action {item.id}: {e}")

        db.commit()


@shared_task(name="sync_calendars_all_users")
def sync_calendars_all_users():
    """Trigger calendar sync for all users with Google or Microsoft connected."""
    import asyncio
    asyncio.run(_sync_calendars_async())


async def _sync_calendars_async():
    from app.models.user import User

    with SessionLocal() as db:
        result = db.execute(select(User).where(User.is_active.is_(True)))
        users = result.scalars().all()

        synced = 0
        for user in users:
            integrations = user.integrations or {}
            google = integrations.get("google", {})
            microsoft = integrations.get("microsoft", {})

            if google.get("access_token") or microsoft.get("access_token"):
                try:
                    from app.services.integrations.google_calendar import sync_user_calendar
                    await sync_user_calendar(db, user)
                    synced += 1
                except ImportError:
                    pass
                except Exception as e:
                    logger.error(f"Calendar sync failed for user {user.id}: {e}")

        logger.info(f"Calendar sync completed for {synced} users")


# ─── Slack helper ────────────────────────────────────────────────────────────

async def _notify_slack(token: str, channel: str, meeting: "Meeting", action_count: int, decision_count: int):
    """Post a meeting summary card to Slack using the user's bot token."""
    import httpx
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"📋 Meeting Completed: {meeting.title}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": meeting.summary or "_No summary generated._"},
        },
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"*{decision_count}* decisions  •  *{action_count}* action items"},
            ],
        },
    ]
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {token}"},
            json={"channel": channel, "blocks": blocks, "text": f"Meeting completed: {meeting.title}"},
        )


# ─── Linear helper ───────────────────────────────────────────────────────────

async def _create_jira_issues(
    jira_url: str,
    username: str,
    api_token: str,
    project_key: str,
    meeting_title: str,
    action_items: list,
):
    """Create Jira tasks for each extracted action item."""
    import base64
    import httpx

    credentials = base64.b64encode(f"{username}:{api_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    jira_url = jira_url.rstrip("/")

    async with httpx.AsyncClient(timeout=15) as client:
        for item in action_items[:10]:
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": item.title,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"From meeting: {meeting_title}\n\n{item.description or ''}",
                                    }
                                ],
                            }
                        ],
                    },
                    "issuetype": {"name": "Task"},
                }
            }
            try:
                resp = await client.post(
                    f"{jira_url}/rest/api/3/issue",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"Created Jira issue: {data.get('key')} for action: {item.title}")
            except Exception as e:
                logger.warning(f"Failed to create Jira issue for '{item.title}': {e}")


async def _create_asana_tasks(
    access_token: str,
    workspace_gid: str,
    project_gid: Optional[str],
    meeting_title: str,
    action_items: list,
):
    """Create Asana tasks for each extracted action item."""
    import httpx

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        for item in action_items[:10]:
            payload: dict = {
                "data": {
                    "name": item.title,
                    "notes": f"From meeting: {meeting_title}\n\n{item.description or ''}",
                    "workspace": workspace_gid,
                }
            }
            if project_gid:
                payload["data"]["projects"] = [project_gid]

            try:
                resp = await client.post(
                    "https://app.asana.com/api/1.0/tasks",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                logger.info(f"Created Asana task: {data.get('gid')} for action: {item.title}")
            except Exception as e:
                logger.warning(f"Failed to create Asana task for '{item.title}': {e}")


async def _create_linear_issues(api_key: str, meeting_title: str, action_items: list):
    """Create Linear issues for each extracted action item."""
    import httpx

    # First, get the first available team id
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": api_key, "Content-Type": "application/json"},
            json={"query": "{ teams { nodes { id name } } }"},
        )
    teams = r.json().get("data", {}).get("teams", {}).get("nodes", [])
    if not teams:
        logger.warning("No Linear teams found - skipping issue creation")
        return

    team_id = teams[0]["id"]

    async with httpx.AsyncClient() as client:
        for item in action_items[:10]:  # cap at 10 to avoid flooding
            mutation = """
            mutation CreateIssue($teamId: String!, $title: String!, $description: String) {
              issueCreate(input: { teamId: $teamId, title: $title, description: $description }) {
                success
                issue { id identifier url }
              }
            }
            """
            desc = f"Auto-created from meeting: **{meeting_title}**\n\n{item.description or ''}"
            await client.post(
                "https://api.linear.app/graphql",
                headers={"Authorization": api_key, "Content-Type": "application/json"},
                json={"query": mutation, "variables": {"teamId": team_id, "title": item.title, "description": desc}},
            )
            logger.info(f"Created Linear issue for action: {item.title}")
