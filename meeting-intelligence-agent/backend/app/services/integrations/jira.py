"""
Jira Integration Service
"""
import logging
from typing import Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

PRIORITY_MAP = {
    "urgent": "Highest",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
}


class JiraService:
    """Service for Jira integration using Jira REST API v3."""

    def __init__(self):
        self.jira_url = settings.JIRA_URL.rstrip("/")
        self.username = settings.JIRA_USERNAME
        self.api_token = settings.JIRA_API_TOKEN

    def _headers(self) -> Dict[str, str]:
        import base64
        credentials = base64.b64encode(
            f"{self.username}:{self.api_token}".encode()
        ).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _is_configured(self) -> bool:
        return bool(self.jira_url and self.username and self.api_token)

    async def create_issue(
        self,
        title: str,
        description: str,
        project_key: str,
        assignee_email: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[str] = None,
    ) -> Optional[Dict]:
        """Create a Jira issue."""
        if not self._is_configured():
            logger.warning("Jira not configured — skipping issue creation")
            return None

        payload: Dict = {
            "fields": {
                "project": {"key": project_key},
                "summary": title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}],
                        }
                    ],
                },
                "issuetype": {"name": "Task"},
                "priority": {"name": PRIORITY_MAP.get(priority, "Medium")},
            }
        }

        if due_date:
            payload["fields"]["duedate"] = due_date

        if assignee_email:
            account_id = await self._get_account_id(assignee_email)
            if account_id:
                payload["fields"]["assignee"] = {"accountId": account_id}

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.post(
                    f"{self.jira_url}/rest/api/3/issue",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"Created Jira issue: {data.get('key')}")
                return {
                    "id": data.get("id"),
                    "key": data.get("key"),
                    "url": f"{self.jira_url}/browse/{data.get('key')}",
                }
            except httpx.HTTPStatusError as e:
                logger.error(f"Jira API error creating issue: {e.response.text}")
                return None
            except httpx.HTTPError as e:
                logger.error(f"Jira connection error: {e}")
                return None

    async def get_issue(self, issue_key: str) -> Optional[Dict]:
        """Get a Jira issue by key."""
        if not self._is_configured():
            return None

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.get(
                    f"{self.jira_url}/rest/api/3/issue/{issue_key}",
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()
                fields = data.get("fields", {})
                return {
                    "key": data.get("key"),
                    "summary": fields.get("summary"),
                    "status": fields.get("status", {}).get("name"),
                    "assignee": (fields.get("assignee") or {}).get("displayName"),
                    "url": f"{self.jira_url}/browse/{data.get('key')}",
                }
            except httpx.HTTPError as e:
                logger.error(f"Failed to get Jira issue {issue_key}: {e}")
                return None

    async def update_issue_status(self, issue_key: str, transition_name: str) -> bool:
        """Transition a Jira issue to a new status by transition name."""
        if not self._is_configured():
            return False

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                # Get available transitions
                resp = await client.get(
                    f"{self.jira_url}/rest/api/3/issue/{issue_key}/transitions",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                transitions = resp.json().get("transitions", [])

                transition_id = next(
                    (t["id"] for t in transitions if t["name"].lower() == transition_name.lower()),
                    None,
                )
                if not transition_id:
                    logger.warning(f"Transition '{transition_name}' not found for {issue_key}")
                    return False

                resp2 = await client.post(
                    f"{self.jira_url}/rest/api/3/issue/{issue_key}/transitions",
                    headers=self._headers(),
                    json={"transition": {"id": transition_id}},
                )
                resp2.raise_for_status()
                return True
            except httpx.HTTPError as e:
                logger.error(f"Failed to update Jira issue status: {e}")
                return False

    async def get_projects(self) -> List[Dict]:
        """List accessible Jira projects."""
        if not self._is_configured():
            return []

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.get(
                    f"{self.jira_url}/rest/api/3/project/search",
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()
                return [
                    {"key": p["key"], "name": p["name"], "id": p["id"]}
                    for p in data.get("values", [])
                ]
            except httpx.HTTPError as e:
                logger.error(f"Failed to list Jira projects: {e}")
                return []

    async def test_connection(self) -> bool:
        """Verify Jira credentials are valid."""
        if not self._is_configured():
            return False

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(
                    f"{self.jira_url}/rest/api/3/myself",
                    headers=self._headers(),
                )
                return response.status_code == 200
            except httpx.HTTPError:
                return False

    async def _get_account_id(self, email: str) -> Optional[str]:
        """Resolve a user email to a Jira accountId."""
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(
                    f"{self.jira_url}/rest/api/3/user/search",
                    headers=self._headers(),
                    params={"query": email},
                )
                response.raise_for_status()
                users = response.json()
                if users:
                    return users[0].get("accountId")
            except httpx.HTTPError:
                pass
        return None


jira_service = JiraService()
