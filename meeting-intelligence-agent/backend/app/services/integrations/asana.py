"""
Asana Integration Service
"""
import logging
from typing import Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

PRIORITY_TAG_MAP = {
    "urgent": "Urgent",
    "high": "High Priority",
    "medium": "Medium Priority",
    "low": "Low Priority",
}


class AsanaService:
    """Service for Asana integration using Asana REST API v1."""

    BASE_URL = "https://app.asana.com/api/1.0"

    def __init__(self):
        self.access_token = settings.ASANA_ACCESS_TOKEN

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _is_configured(self) -> bool:
        return bool(self.access_token)

    async def create_task(
        self,
        name: str,
        notes: str,
        workspace_gid: str,
        project_gid: Optional[str] = None,
        assignee_email: Optional[str] = None,
        due_on: Optional[str] = None,
    ) -> Optional[Dict]:
        """Create a task in Asana."""
        if not self._is_configured():
            logger.warning("Asana not configured — skipping task creation")
            return None

        payload: Dict = {
            "data": {
                "name": name,
                "notes": notes,
                "workspace": workspace_gid,
            }
        }

        if project_gid:
            payload["data"]["projects"] = [project_gid]
        if due_on:
            payload["data"]["due_on"] = due_on
        if assignee_email:
            payload["data"]["assignee"] = assignee_email

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}/tasks",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json().get("data", {})
                logger.info(f"Created Asana task: {data.get('gid')} — {name}")
                return {
                    "gid": data.get("gid"),
                    "name": data.get("name"),
                    "url": f"https://app.asana.com/0/{project_gid or workspace_gid}/{data.get('gid')}",
                }
            except httpx.HTTPStatusError as e:
                logger.error(f"Asana API error creating task: {e.response.text}")
                return None
            except httpx.HTTPError as e:
                logger.error(f"Asana connection error: {e}")
                return None

    async def get_task(self, task_gid: str) -> Optional[Dict]:
        """Get an Asana task by GID."""
        if not self._is_configured():
            return None

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/tasks/{task_gid}",
                    headers=self._headers(),
                    params={"opt_fields": "gid,name,notes,completed,assignee.name,due_on"},
                )
                response.raise_for_status()
                data = response.json().get("data", {})
                return {
                    "gid": data.get("gid"),
                    "name": data.get("name"),
                    "completed": data.get("completed"),
                    "assignee": (data.get("assignee") or {}).get("name"),
                    "due_on": data.get("due_on"),
                }
            except httpx.HTTPError as e:
                logger.error(f"Failed to get Asana task {task_gid}: {e}")
                return None

    async def complete_task(self, task_gid: str) -> bool:
        """Mark an Asana task as complete."""
        if not self._is_configured():
            return False

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.put(
                    f"{self.BASE_URL}/tasks/{task_gid}",
                    headers=self._headers(),
                    json={"data": {"completed": True}},
                )
                response.raise_for_status()
                return True
            except httpx.HTTPError as e:
                logger.error(f"Failed to complete Asana task {task_gid}: {e}")
                return False

    async def list_workspaces(self) -> List[Dict]:
        """List accessible Asana workspaces."""
        if not self._is_configured():
            return []

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/workspaces",
                    headers=self._headers(),
                )
                response.raise_for_status()
                return [
                    {"gid": w["gid"], "name": w["name"]}
                    for w in response.json().get("data", [])
                ]
            except httpx.HTTPError as e:
                logger.error(f"Failed to list Asana workspaces: {e}")
                return []

    async def list_projects(self, workspace_gid: str) -> List[Dict]:
        """List projects in a workspace."""
        if not self._is_configured():
            return []

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/projects",
                    headers=self._headers(),
                    params={"workspace": workspace_gid, "opt_fields": "gid,name"},
                )
                response.raise_for_status()
                return [
                    {"gid": p["gid"], "name": p["name"]}
                    for p in response.json().get("data", [])
                ]
            except httpx.HTTPError as e:
                logger.error(f"Failed to list Asana projects: {e}")
                return []

    async def test_connection(self) -> bool:
        """Verify Asana token is valid."""
        if not self._is_configured():
            return False

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/users/me",
                    headers=self._headers(),
                )
                return response.status_code == 200
            except httpx.HTTPError:
                return False


asana_service = AsanaService()
