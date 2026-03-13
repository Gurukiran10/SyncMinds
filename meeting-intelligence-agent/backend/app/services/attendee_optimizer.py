"""
Attendee Optimizer Service
Pre-meeting: suggests who to add based on agenda topics.
Post-meeting: flags attendees with zero participation.
"""
import logging
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.action_item import ActionItem
from app.models.meeting import Meeting
from app.models.transcript import Transcript
from app.models.user import User

logger = logging.getLogger(__name__)


class AttendeeOptimizer:

    def analyze(self, db: Session, meeting: Meeting) -> Dict[str, Any]:
        """Run both pre- and post-meeting analyses and return combined result."""
        result: Dict[str, Any] = {
            "meeting_id": str(meeting.id),
            "meeting_title": meeting.title,
        }

        if meeting.status in ("scheduled", "in_progress"):
            result["type"] = "pre_meeting"
            result["suggestions"] = self._suggest_attendees(db, meeting)
        else:
            result["type"] = "post_meeting"
            result["unnecessary_attendees"] = self._flag_unnecessary_attendees(db, meeting)

        return result

    def _suggest_attendees(self, db: Session, meeting: Meeting) -> List[Dict[str, Any]]:
        """
        Suggest users to add based on agenda topic overlap with past meetings.
        Returns users NOT already in the attendee list who contributed to similar topics.
        """
        agenda_items = meeting.agenda or []
        if not agenda_items:
            return []

        agenda_text = " ".join(
            item if isinstance(item, str) else item.get("text", "")
            for item in agenda_items
        ).lower()

        current_attendee_ids = set(str(aid) for aid in (meeting.attendee_ids or []))
        current_attendee_ids.add(str(meeting.organizer_id))

        all_meetings = db.execute(select(Meeting).where(Meeting.status == "completed")).scalars().all()

        # Score users by topic overlap
        user_scores: Dict[str, float] = {}
        for past_meeting in all_meetings:
            if str(past_meeting.id) == str(meeting.id):
                continue

            topics = past_meeting.discussion_topics or []
            topic_text = " ".join(str(t) for t in topics).lower()

            # Simple word overlap score
            agenda_words = set(agenda_text.split())
            topic_words = set(topic_text.split())
            overlap = len(agenda_words & topic_words)
            if overlap == 0:
                continue

            # Credit all attendees of this past meeting
            for uid in (past_meeting.attendee_ids or []):
                uid_str = str(uid)
                if uid_str not in current_attendee_ids:
                    user_scores[uid_str] = user_scores.get(uid_str, 0) + overlap

        if not user_scores:
            return []

        # Fetch top 5 suggested users
        top_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        suggestions = []
        for uid, score in top_users:
            user = db.execute(select(User).where(User.id == uid)).scalar_one_or_none()
            if user and user.is_active:
                suggestions.append({
                    "user_id": uid,
                    "full_name": user.full_name,
                    "email": user.email,
                    "relevance_score": round(score, 2),
                    "reason": "Contributed to similar topics in past meetings",
                })

        return suggestions

    def _flag_unnecessary_attendees(self, db: Session, meeting: Meeting) -> List[Dict[str, Any]]:
        """
        Post-meeting: identify attendees who had zero speaking segments
        and zero action items assigned to them.
        """
        attendee_ids = [str(aid) for aid in (meeting.attendee_ids or [])]
        if not attendee_ids:
            return []

        # Get speaker IDs from transcripts
        transcripts = db.execute(
            select(Transcript).where(Transcript.meeting_id == meeting.id)
        ).scalars().all()
        speakers_seen = set(str(t.speaker_id) for t in transcripts if t.speaker_id)

        # Get action item owners
        action_items = db.execute(
            select(ActionItem).where(ActionItem.meeting_id == meeting.id)
        ).scalars().all()
        action_owners = set(str(a.owner_id) for a in action_items if a.owner_id)

        unnecessary = []
        for uid in attendee_ids:
            if uid == str(meeting.organizer_id):
                continue
            if uid not in speakers_seen and uid not in action_owners:
                user = db.execute(select(User).where(User.id == uid)).scalar_one_or_none()
                if user:
                    unnecessary.append({
                        "user_id": uid,
                        "full_name": user.full_name,
                        "email": user.email,
                        "reason": "No speaking turns and no action items assigned",
                    })

        return unnecessary


def compute_meeting_quality_score(
    executive_summary: str,
    decisions: list,
    action_items: list,
    sentiment_score: float,
    duration_minutes: float,
    attendee_count: int,
) -> float:
    """
    Compute a 0-100 quality score for a meeting based on outcomes.

    Factors:
    - Decision rate: decisions per hour (target >= 2)
    - Action rate: action items per hour (target >= 3)
    - Sentiment: positive meetings score higher
    - Efficiency: penalise long meetings with few outcomes
    - Has summary: +10 points for non-empty summary
    """
    if duration_minutes <= 0:
        duration_minutes = 60

    hours = duration_minutes / 60.0
    decision_rate = len(decisions) / hours
    action_rate = len(action_items) / hours

    # Normalise each component to 0-25
    decision_score = min(25.0, (decision_rate / 2.0) * 25.0)
    action_score = min(25.0, (action_rate / 3.0) * 25.0)

    # Sentiment: -1..1 → 0..25
    sentiment_score_clamped = max(-1.0, min(1.0, sentiment_score or 0.0))
    sentiment_component = ((sentiment_score_clamped + 1) / 2) * 25.0

    # Efficiency: penalise meetings > 60 min with < 2 total outcomes
    total_outcomes = len(decisions) + len(action_items)
    if duration_minutes > 60 and total_outcomes < 2:
        efficiency_component = 10.0
    elif duration_minutes <= 30 and total_outcomes >= 2:
        efficiency_component = 25.0
    else:
        efficiency_component = 20.0

    score = decision_score + action_score + sentiment_component + efficiency_component

    # Bonus: non-empty summary
    if executive_summary and len(executive_summary.strip()) > 50:
        score = min(100.0, score + 5.0)

    return round(min(100.0, max(0.0, score)), 1)
