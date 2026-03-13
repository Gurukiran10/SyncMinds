"""
Slack Integration Service
"""
import logging
from typing import Any
from typing import Dict, List, Optional
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from app.core.config import settings

logger = logging.getLogger(__name__)


class SlackService:
    """Service for Slack integration"""
    
    def __init__(self):
        self.client = AsyncWebClient(token=settings.SLACK_BOT_TOKEN) if settings.SLACK_BOT_TOKEN else None
    
    async def send_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None,
    ) -> Dict:
        """Send message to Slack channel"""
        if not self.client:
            logger.warning("Slack client not configured")
            return {}
        
        try:
            response = await self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks,
                thread_ts=thread_ts,
            )
            return response.data  # type: ignore
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            raise
    
    async def send_mention_alert(
        self,
        user_id: str,
        mention_data: Dict,
        meeting_title: str,
    ) -> Dict:
        """Send personalized mention alert"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔔 You were mentioned in: {meeting_title}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Mention Type:* {mention_data['type']}\n*Relevance:* {mention_data['relevance_score']}/100",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Context:*\n> {mention_data['text']}",
                },
            },
        ]
        
        if mention_data.get("is_action_item"):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "⚠️ *This appears to be an action item for you*",
                },
            })
        
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Full Summary",
                    },
                    "url": f"https://app.meetingintel.ai/meetings/{mention_data['meeting_id']}",
                    "style": "primary",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Dismiss",
                    },
                    "value": f"dismiss_{mention_data['id']}",
                },
            ],
        })
        
        return await self.send_message(
            channel=user_id,
            text=f"You were mentioned in {meeting_title}",
            blocks=blocks,
        )

    def _build_mention_alert_blocks(
        self,
        mention_data: Dict[str, Any],
        meeting_title: str,
        meeting_url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        mention_type = str(mention_data.get("mention_type") or mention_data.get("type") or "contextual").replace("_", " ").title()
        relevance = mention_data.get("relevance_score", 0)
        urgency = mention_data.get("urgency_score")
        context_text = mention_data.get("context") or mention_data.get("full_context") or mention_data.get("text") or ""

        blocks: List[Dict[str, Any]] = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🔔 You were mentioned in: {meeting_title}"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Type:*\n{mention_type}"},
                    {"type": "mrkdwn", "text": f"*Relevance:*\n{relevance}/100"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Context:*\n> {context_text[:1200]}"},
            },
        ]

        action_item_id = mention_data.get("action_item_id")
        owner = mention_data.get("owner")
        dependency = mention_data.get("dependency")
        due_date = mention_data.get("due_date")
        status = mention_data.get("status")

        detail_fields: List[Dict[str, Any]] = []
        if action_item_id:
            detail_fields.append({"type": "mrkdwn", "text": f"*Action Item:*\n#{str(action_item_id)[:8]}"})
        detail_fields.append({"type": "mrkdwn", "text": f"*Meeting:*\n{meeting_title}"})
        if owner:
            detail_fields.append({"type": "mrkdwn", "text": f"*Owner:*\n{owner}"})
        if dependency:
            detail_fields.append({"type": "mrkdwn", "text": f"*Dependency:*\n{dependency}"})
        if due_date:
            detail_fields.append({"type": "mrkdwn", "text": f"*Due Date:*\n{due_date}"})
        if status:
            detail_fields.append({"type": "mrkdwn", "text": f"*Status:*\n{status}"})

        if detail_fields:
            blocks.insert(
                2,
                {
                    "type": "section",
                    "fields": detail_fields[:6],
                },
            )

        if urgency is not None:
            blocks.insert(
                3 if detail_fields else 2,
                {"type": "context", "elements": [{"type": "mrkdwn", "text": f"*Urgency:* {urgency}/100"}]},
            )

        if mention_data.get("is_action_item"):
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "⚠️ *This looks like an action assignment for you or your team.*"},
            })

        if mention_data.get("is_question"):
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "❓ *This mention may need your response.*"},
            })

        if mention_data.get("mention_type") == "feedback":
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "🎉 *This looks like praise or positive feedback.*"},
            })

        if mention_data.get("mention_type") == "resource_request":
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "🧰 *This looks like a resource or support request affecting you or your team.*"},
            })

        if meeting_url:
            blocks.append(
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View Meeting"},
                            "url": meeting_url,
                            "style": "primary",
                        }
                    ],
                }
            )

        return blocks

    async def send_mention_alert_via_token(
        self,
        bot_token: str,
        recipient_email: str,
        mention_data: Dict[str, Any],
        meeting_title: str,
        meeting_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a real-time mention alert as a DM using a provided Slack bot token."""
        client = AsyncWebClient(token=bot_token)
        try:
            lookup = await client.users_lookupByEmail(email=recipient_email)
            user = lookup.data.get("user") or {}
            slack_user_id = user.get("id")
            if not slack_user_id:
                raise SlackApiError(message="Slack user not found", response=lookup)

            convo = await client.conversations_open(users=[slack_user_id])
            channel_id = (convo.data.get("channel") or {}).get("id")
            if not channel_id:
                raise SlackApiError(message="Failed to open DM channel", response=convo)

            blocks = self._build_mention_alert_blocks(mention_data, meeting_title, meeting_url=meeting_url)
            response = await client.chat_postMessage(
                channel=channel_id,
                text=f"You were mentioned in {meeting_title}",
                blocks=blocks,
            )
            return response.data  # type: ignore
        except SlackApiError as e:
            logger.error(f"Slack mention alert failed for {recipient_email}: {e.response.get('error') if hasattr(e, 'response') else e}")
            raise

    async def send_blocks_via_token(
        self,
        bot_token: str,
        recipient_email: str,
        text: str,
        blocks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Send a DM using a provided bot token and custom Slack blocks."""
        client = AsyncWebClient(token=bot_token)
        try:
            lookup = await client.users_lookupByEmail(email=recipient_email)
            user = lookup.data.get("user") or {}
            slack_user_id = user.get("id")
            if not slack_user_id:
                raise SlackApiError(message="Slack user not found", response=lookup)

            convo = await client.conversations_open(users=[slack_user_id])
            channel_id = (convo.data.get("channel") or {}).get("id")
            if not channel_id:
                raise SlackApiError(message="Failed to open DM channel", response=convo)

            response = await client.chat_postMessage(
                channel=channel_id,
                text=text,
                blocks=blocks,
            )
            return response.data  # type: ignore
        except SlackApiError as e:
            logger.error(f"Slack DM failed for {recipient_email}: {e.response.get('error') if hasattr(e, 'response') else e}")
            raise
    
    async def send_meeting_summary(
        self,
        channel: str,
        summary_data: Dict,
    ) -> Dict:
        """Send meeting summary to channel"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📝 Meeting Summary: {summary_data['title']}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Executive Summary:*\n{summary_data['executive_summary']}",
                },
            },
            {
                "type": "divider",
            },
        ]
        
        # Add decisions
        if summary_data.get("decisions"):
            decisions_text = "\n".join([
                f"• {d['decision']}"
                for d in summary_data["decisions"][:3]
            ])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Key Decisions:*\n{decisions_text}",
                },
            })
        
        # Add action items
        if summary_data.get("action_items"):
            action_text = "\n".join([
                f"• {a['title']} - @{a['owner']} {'🔴' if a['priority'] == 'high' else '🟡' if a['priority'] == 'medium' else '🟢'}"
                for a in summary_data["action_items"][:5]
            ])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Action Items:*\n{action_text}",
                },
            })
        
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Full Summary",
                    },
                    "url": f"https://app.meetingintel.ai/meetings/{summary_data['meeting_id']}",
                    "style": "primary",
                },
            ],
        })
        
        return await self.send_message(
            channel=channel,
            text=f"Meeting summary: {summary_data['title']}",
            blocks=blocks,
        )
    
    async def send_action_reminder(
        self,
        user_id: str,
        action_item: Dict,
    ) -> Dict:
        """Send action item reminder"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⏰ Action Item Reminder",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{action_item['title']}*\n\n{action_item['description']}",
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Due Date:*\n{action_item['due_date']}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Priority:*\n{action_item['priority'].upper()}",
                    },
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✓ Mark Complete",
                        },
                        "value": f"complete_{action_item['id']}",
                        "style": "primary",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Snooze 1 Day",
                        },
                        "value": f"snooze_{action_item['id']}",
                    },
                ],
            },
        ]
        
        return await self.send_message(
            channel=user_id,
            text=f"Action reminder: {action_item['title']}",
            blocks=blocks,
        )
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get Slack user by email"""
        if not self.client:
            return None
        
        try:
            response = await self.client.users_lookupByEmail(email=email)
            return response.data.get("user")  # type: ignore
        except SlackApiError:
            return None


# Global instance
slack_service = SlackService()
