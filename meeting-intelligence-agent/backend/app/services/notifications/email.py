"""
Email Notification Service using Resend
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def _is_configured() -> bool:
    return bool(settings.RESEND_API_KEY)


async def _send(subject: str, html: str, to: str) -> bool:
    """Send an email via Resend."""
    if not _is_configured():
        logger.warning("Resend API key not configured — skipping email")
        return False

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(
                RESEND_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": settings.FROM_EMAIL,
                    "to": [to],
                    "subject": subject,
                    "html": html,
                },
            )
            response.raise_for_status()
            logger.info(f"Email sent to {to}: {subject}")
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Resend API error: {e.response.text}")
            return False
        except httpx.HTTPError as e:
            logger.error(f"Email send failed: {e}")
            return False


async def send_pre_meeting_brief(
    user_email: str,
    user_name: str,
    meeting_title: str,
    meeting_time: str,
    open_actions: List[Dict],
    suggested_points: List[str],
    skip_recommendation: str,
    meeting_url: str,
) -> bool:
    """Send a pre-meeting intelligence brief via email."""
    actions_html = "".join(
        f"<li><b>{a.get('title', '')}</b> — due {a.get('due_date', 'no date')}</li>"
        for a in open_actions[:5]
    )
    points_html = "".join(f"<li>{p}</li>" for p in suggested_points[:5])

    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
      <h2 style="color:#1a1a2e;">Pre-Meeting Brief: {meeting_title}</h2>
      <p style="color:#666;">Meeting at <b>{meeting_time}</b></p>

      <div style="background:#f0f4ff;padding:12px;border-radius:8px;margin:16px 0;">
        <b>Attendance:</b> {skip_recommendation}
      </div>

      {"<h3>Your Open Action Items</h3><ul>" + actions_html + "</ul>" if open_actions else ""}
      {"<h3>Suggested Talking Points</h3><ul>" + points_html + "</ul>" if suggested_points else ""}

      <p>
        <a href="{meeting_url}" style="background:#4f46e5;color:#fff;padding:10px 20px;
           border-radius:6px;text-decoration:none;display:inline-block;margin-top:16px;">
          View Full Brief
        </a>
      </p>
      <hr style="margin-top:32px;border:none;border-top:1px solid #eee;">
      <p style="color:#999;font-size:12px;">SyncMinds Meeting Intelligence</p>
    </div>
    """
    return await _send(
        subject=f"Pre-Meeting Brief: {meeting_title}",
        html=html,
        to=user_email,
    )


async def send_post_meeting_summary(
    user_email: str,
    meeting_title: str,
    executive_summary: str,
    decisions: List[Dict],
    action_items: List[Dict],
    meeting_url: str,
) -> bool:
    """Send a post-meeting summary via email."""
    decisions_html = "".join(
        f"<li><b>{d.get('decision', '')}</b> — {d.get('decision_maker', 'unknown')}</li>"
        for d in decisions[:5]
    )
    actions_html = "".join(
        f"<li><b>{a.get('title', '')}</b> ({a.get('owner', 'unassigned')}) — due {a.get('due_date', 'TBD')}</li>"
        for a in action_items[:5]
    )

    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
      <h2 style="color:#1a1a2e;">Meeting Summary: {meeting_title}</h2>

      <div style="background:#f9fafb;padding:16px;border-radius:8px;margin:16px 0;">
        <p>{executive_summary}</p>
      </div>

      {"<h3>Key Decisions</h3><ul>" + decisions_html + "</ul>" if decisions else ""}
      {"<h3>Action Items</h3><ul>" + actions_html + "</ul>" if action_items else ""}

      <p>
        <a href="{meeting_url}" style="background:#4f46e5;color:#fff;padding:10px 20px;
           border-radius:6px;text-decoration:none;display:inline-block;margin-top:16px;">
          View Full Summary
        </a>
      </p>
      <hr style="margin-top:32px;border:none;border-top:1px solid #eee;">
      <p style="color:#999;font-size:12px;">SyncMinds Meeting Intelligence</p>
    </div>
    """
    return await _send(
        subject=f"Meeting Summary: {meeting_title}",
        html=html,
        to=user_email,
    )


async def send_action_reminder(
    user_email: str,
    user_name: str,
    action_title: str,
    due_date: str,
    priority: str,
    overdue: bool = False,
    action_url: str = "",
) -> bool:
    """Send an action item reminder email."""
    status_label = "OVERDUE" if overdue else "Due Soon"
    status_color = "#dc2626" if overdue else "#d97706"

    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
      <div style="background:{status_color};color:#fff;padding:8px 16px;border-radius:6px;
                  display:inline-block;font-size:12px;font-weight:bold;">{status_label}</div>

      <h2 style="color:#1a1a2e;margin-top:16px;">Action Item Reminder</h2>
      <h3 style="color:#374151;">{action_title}</h3>

      <table style="width:100%;border-collapse:collapse;margin:16px 0;">
        <tr>
          <td style="padding:8px;color:#666;width:120px;">Due Date</td>
          <td style="padding:8px;font-weight:bold;">{due_date}</td>
        </tr>
        <tr style="background:#f9fafb;">
          <td style="padding:8px;color:#666;">Priority</td>
          <td style="padding:8px;font-weight:bold;">{priority.title()}</td>
        </tr>
      </table>

      {f'<p><a href="{action_url}" style="background:#4f46e5;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;display:inline-block;">View Action Item</a></p>' if action_url else ""}

      <hr style="margin-top:32px;border:none;border-top:1px solid #eee;">
      <p style="color:#999;font-size:12px;">SyncMinds Meeting Intelligence</p>
    </div>
    """
    subject = f"{'[OVERDUE] ' if overdue else ''}Action Item: {action_title}"
    return await _send(subject=subject, html=html, to=user_email)


async def send_catch_up_summary(
    user_email: str,
    meeting_title: str,
    mention_count: int,
    actions_assigned: List[Dict],
    decisions_affecting: List[Dict],
    meeting_url: str,
) -> bool:
    """Send an absence catch-up summary email."""
    actions_html = "".join(
        f"<li><b>{a.get('title', '')}</b> — due {a.get('due_date', 'TBD')}</li>"
        for a in actions_assigned[:5]
    )
    decisions_html = "".join(
        f"<li>{d.get('decision', '')}</li>"
        for d in decisions_affecting[:5]
    )

    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
      <h2 style="color:#1a1a2e;">You missed: {meeting_title}</h2>

      <div style="background:#fef3c7;padding:12px;border-radius:8px;margin:16px 0;">
        You were mentioned <b>{mention_count} time{"s" if mention_count != 1 else ""}</b> in this meeting.
      </div>

      {"<h3>Actions Assigned to You</h3><ul>" + actions_html + "</ul>" if actions_assigned else ""}
      {"<h3>Decisions Affecting Your Work</h3><ul>" + decisions_html + "</ul>" if decisions_affecting else ""}

      <p>
        <a href="{meeting_url}" style="background:#4f46e5;color:#fff;padding:10px 20px;
           border-radius:6px;text-decoration:none;display:inline-block;margin-top:16px;">
          View Full Catch-Up
        </a>
      </p>
      <hr style="margin-top:32px;border:none;border-top:1px solid #eee;">
      <p style="color:#999;font-size:12px;">SyncMinds Meeting Intelligence</p>
    </div>
    """
    return await _send(
        subject=f"Catch-Up: {meeting_title}",
        html=html,
        to=user_email,
    )
