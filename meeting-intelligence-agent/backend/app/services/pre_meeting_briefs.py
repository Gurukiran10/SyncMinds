"""
Pre-Meeting Intelligence Briefs Service
Generates personalized meeting preparation briefs 30 minutes before meetings
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from app.models.action_item import ActionItem
from app.models.meeting import Meeting
from app.models.user import User
from app.models.mention import Mention
from app.services.ai.nlp import nlp_service
from app.services.integrations.slack import slack_service

logger = logging.getLogger(__name__)


class PreMeetingBriefService:
    """Service for generating pre-meeting intelligence briefs"""

    async def generate_brief_for_user(
        self,
        db: Session,
        meeting: Meeting,
        user: User,
    ) -> Dict[str, Any]:
        """Generate a personalized pre-meeting brief for a user"""

        # Meeting Context
        meeting_context = await self._get_meeting_context(db, meeting, user)

        # Your Preparation
        preparation = await self._get_preparation_items(db, meeting, user)

        # Recent Developments
        developments = await self._get_recent_developments(db, meeting, user)

        # Suggested Points
        suggestions = await self._get_suggested_points(db, meeting, user)

        # Time Optimization
        time_optimization = await self._get_time_optimization(db, meeting, user)

        brief = {
            "meeting_id": str(meeting.id),
            "meeting_title": meeting.title,
            "scheduled_start": (lambda d: d.isoformat() if d is not None else None)(getattr(meeting, "scheduled_start", None)),
            "meeting_context": meeting_context,
            "your_preparation": preparation,
            "recent_developments": developments,
            "suggested_points": suggestions,
            "time_optimization": time_optimization,
            "generated_at": datetime.utcnow().isoformat(),
        }

        return brief

    async def _get_meeting_context(self, db: Session, meeting: Meeting, user: User) -> Dict[str, Any]:
        """Get meeting context information"""
        attendees = []
        if getattr(meeting, "attendee_ids", None) is not None:
            for attendee_id in (getattr(meeting, "attendee_ids", None) or []):
                attendee = db.execute(
                    select(User).where(User.id == attendee_id)
                ).scalar_one_or_none()
                if attendee:
                    attendees.append({
                        "name": attendee.full_name or attendee.username,
                        "role": attendee.job_title or attendee.role or "member",
                        "department": attendee.department,
                    })

        # Last meeting of this group
        last_meeting = None
        _attendee_ids = list(getattr(meeting, "attendee_ids", None) or [])
        if _attendee_ids:
            last_meeting = db.execute(
                select(Meeting).where(
                    and_(
                        Meeting.id != getattr(meeting, "id", None),
                        Meeting.scheduled_start < getattr(meeting, "scheduled_start", None),
                        or_(*[Meeting.attendee_ids.contains([str(aid)]) for aid in _attendee_ids])
                    )
                ).order_by(Meeting.scheduled_start.desc())
            ).scalar_one_or_none()

        return {
            "purpose": meeting.description or "Meeting scheduled",
            "agenda": meeting.agenda or [],
            "attendees": attendees,
            "last_group_meeting": {
                "title": last_meeting.title if last_meeting else None,
                "date": (lambda d: d.isoformat() if d is not None else None)(getattr(last_meeting, "scheduled_start", None) if last_meeting else None),
                "summary": last_meeting.summary if last_meeting else None,
            } if last_meeting else None,
        }

    async def _get_preparation_items(self, db: Session, meeting: Meeting, user: User) -> Dict[str, Any]:
        """Get user's preparation items"""
        # Open action items owned by user
        open_actions = db.execute(
            select(ActionItem).where(
                and_(
                    ActionItem.owner_id == user.id,
                    ActionItem.status.in_(["open", "in_progress"]),
                    or_(
                        ActionItem.due_date.is_(None),
                        ActionItem.due_date >= datetime.utcnow()
                    )
                )
            )
        ).scalars().all()

        # Decisions pending user input (mentions in recent meetings)
        recent_mentions = db.execute(
            select(Mention).where(
                and_(
                    Mention.user_id == user.id,
                    Mention.created_at >= datetime.utcnow() - timedelta(days=7),
                    Mention.is_question == True
                )
            )
        ).scalars().all()

        # Expected questions (based on meeting agenda and user's role)
        expected_questions = await self._infer_expected_questions(meeting, user)

        # Relevant background (this would need integration with Slack/docs - placeholder)
        relevant_background = await self._get_relevant_background(db, meeting, user)

        return {
            "open_action_items": [
                {
                    "id": str(action.id),
                    "title": action.title,
                    "description": action.description,
                    "due_date": (lambda d: d.isoformat() if d is not None else None)(getattr(action, "due_date", None)),
                    "priority": action.priority,
                }
                for action in open_actions[:5]
            ],
            "decisions_pending_input": [
                {
                    "meeting_title": mention.meeting.title if mention.meeting else "Unknown",
                    "question": mention.mentioned_text,
                    "context": mention.full_context,
                }
                for mention in recent_mentions[:3]
            ],
            "expected_questions": expected_questions,
            "relevant_background": relevant_background,
        }

    async def _get_recent_developments(self, db: Session, meeting: Meeting, user: User) -> Dict[str, Any]:
        """Get recent developments since scheduling"""
        # Recent mentions of user's projects/areas
        recent_mentions = db.execute(
            select(Mention).where(
                and_(
                    Mention.user_id == user.id,
                    Mention.created_at >= (getattr(meeting, "created_at", None) or datetime.utcnow() - timedelta(days=1))
                )
            )
        ).scalars().all()

        # Recent action items related to user's areas
        # This is simplified - would need better matching logic
        related_actions = db.execute(
            select(ActionItem).where(
                and_(
                    ActionItem.created_at >= (getattr(meeting, "created_at", None) or datetime.utcnow() - timedelta(days=1)),
                    ActionItem.owner_id != user.id  # Not owned by user
                )
            )
        ).scalars().all()

        return {
            "related_discussions": [
                {
                    "meeting_title": mention.meeting.title if mention.meeting else "Unknown",
                    "topic": mention.mentioned_text,
                    "type": mention.mention_type,
                }
                for mention in recent_mentions[:3]
            ],
            "related_action_items": [
                {
                    "title": action.title,
                    "owner": action.owner.full_name if action.owner else "Unknown",
                    "status": action.status,
                }
                for action in related_actions[:3]
            ],
            "blockers_to_surface": [],  # Would need more complex logic
        }

    async def _get_suggested_points(self, db: Session, meeting: Meeting, user: User) -> List[str]:
        """Get suggested points for the user to raise"""
        suggestions = []

        # If user owns action items, suggest updates
        open_actions = db.execute(
            select(ActionItem).where(
                and_(
                    ActionItem.owner_id == user.id,
                    ActionItem.status.in_(["open", "in_progress"])
                )
            )
        ).scalars().all()

        if open_actions:
            suggestions.append("Provide updates on your open action items")

        # If user has questions pending, suggest following up
        pending_questions = db.execute(
            select(Mention).where(
                and_(
                    Mention.user_id == user.id,
                    Mention.is_question == True,
                    Mention.created_at >= datetime.utcnow() - timedelta(days=7)
                )
            )
        ).scalars().all()

        if pending_questions:
            suggestions.append("Follow up on questions you raised in recent meetings")

        # Based on user's role and meeting agenda
        _agenda = list(getattr(meeting, "agenda", None) or [])
        _job_title = str(getattr(user, "job_title", "") or "")
        if _agenda and _job_title:
            agenda_text = " ".join(_agenda)
            if "budget" in agenda_text.lower() and ("finance" in _job_title.lower() or "manager" in _job_title.lower()):
                suggestions.append("Be prepared to discuss budget implications")

        return suggestions

    async def _get_time_optimization(self, db: Session, meeting: Meeting, user: User) -> str:
        """Determine if user is critical or optional"""
        # Check if user owns action items discussed in meeting
        user_actions = db.execute(
            select(ActionItem).where(
                and_(
                    ActionItem.owner_id == user.id,
                    ActionItem.meeting_id == meeting.id
                )
            )
        ).scalars().all()

        # Check if user has decision-making mentions
        decision_mentions = db.execute(
            select(Mention).where(
                and_(
                    Mention.user_id == user.id,
                    Mention.meeting_id == meeting.id,
                    or_(
                        Mention.mention_type == "decision_impact",
                        Mention.is_question == True
                    )
                )
            )
        ).scalars().all()

        # Check meeting agenda for critical topics
        critical_topics = ["budget", "decision", "approval", "strategy", "layoff", "hiring"]
        agenda_text = " ".join(list(getattr(meeting, "agenda", None) or [])).lower()
        has_critical_topic = any(topic in agenda_text for topic in critical_topics)

        if user_actions or decision_mentions or has_critical_topic:
            return "Critical: Your input or decisions are needed"
        else:
            return "Optional: Safe to skip if you have other priorities"

    async def _infer_expected_questions(self, meeting: Meeting, user: User) -> List[str]:
        """Infer questions the user might be expected to answer"""
        questions = []

        _infer_agenda = list(getattr(meeting, "agenda", None) or [])
        if _infer_agenda:
            agenda_text = " ".join(_infer_agenda).lower()
            _role = str(getattr(user, "job_title", "") or "")
            if _role:
                role_lower = _role.lower()
                if "engineer" in role_lower and "technical" in agenda_text:
                    questions.append("What are the technical challenges?")
                if "manager" in role_lower and "budget" in agenda_text:
                    questions.append("What is the budget impact?")
                if "designer" in role_lower and "ui" in agenda_text:
                    questions.append("What are the design requirements?")

        return questions

    async def _get_relevant_background(self, db: Session, meeting: Meeting, user: User) -> List[str]:
        """Get relevant background information (placeholder for Slack/docs integration)"""
        # This would integrate with Slack threads, docs, etc.
        # For now, return recent mentions as background
        recent_mentions = db.execute(
            select(Mention).where(
                and_(
                    Mention.user_id == user.id,
                    Mention.created_at >= datetime.utcnow() - timedelta(days=7)
                )
            )
        ).scalars().all()

        return [
            f"Recent discussion: {mention.mentioned_text[:100]}..."
            for mention in recent_mentions[:2]
        ]

    async def send_brief_to_user(
        self,
        db: Session,
        meeting: Meeting,
        user: User,
        brief: Dict[str, Any],
    ) -> bool:
        """Send the brief to the user via Slack"""
        slack_settings = (user.integrations or {}).get("slack", {})
        if not slack_settings.get("bot_token"):
            logger.warning(f"No Slack integration for user {user.email}")
            return False

        try:
            blocks = self._build_brief_blocks(meeting, brief)
            await slack_service.send_mention_alert_via_token(
                bot_token=slack_settings["bot_token"],
                recipient_email=str(getattr(user, "email", "")),
                mention_data={"type": "pre_meeting_brief"},
                meeting_title=str(getattr(meeting, "title", "")),
                meeting_url=f"http://localhost:3000/meetings/{getattr(meeting, 'id', '')}",
            )
            # Actually send the brief
            _username = str(getattr(user, "username", "") or "")
            _email = str(getattr(user, "email", "") or "")
            await slack_service.send_message(
                channel=_username or _email.split("@")[0],
                text=f"📋 Pre-Meeting Brief: {meeting.title}",
                blocks=blocks,
            )
            return True
        except Exception as exc:
            logger.error(f"Failed to send brief to {user.email}: {exc}")
            return False

    def _build_brief_blocks(self, meeting: Meeting, brief: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build Slack blocks for the pre-meeting brief"""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"📋 Pre-Meeting Brief: {meeting.title}"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Scheduled:* {brief['scheduled_start']}\n*Optimization:* {brief['time_optimization']}"},
            },
        ]

        # Meeting Context
        context = brief["meeting_context"]
        if context["purpose"]:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Purpose:* {context['purpose']}"},
            })

        if context["attendees"]:
            attendee_text = "\n".join([f"• {a['name']} ({a['role']})" for a in context["attendees"][:5]])
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Attendees:*\n{attendee_text}"},
            })

        # Your Preparation
        prep = brief["your_preparation"]
        if prep["open_action_items"]:
            action_text = "\n".join([f"• {a['title']}" for a in prep["open_action_items"][:3]])
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Your Open Action Items:*\n{action_text}"},
            })

        # Suggested Points
        if brief["suggested_points"]:
            points_text = "\n".join([f"• {point}" for point in brief["suggested_points"]])
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Suggested Points:*\n{points_text}"},
            })

        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View Full Brief"},
                    "url": f"http://localhost:3000/meetings/{meeting.id}",
                    "style": "primary",
                }
            ],
        })

        return blocks


pre_meeting_brief_service = PreMeetingBriefService()