"""
Linear Integration Service
"""
import logging
from typing import Dict, Optional, List
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LinearService:
    """Service for Linear integration"""
    
    def __init__(self):
        self.api_key = settings.LINEAR_API_KEY
        self.base_url = "https://api.linear.app/graphql"
    
    async def create_issue(
        self,
        title: str,
        description: str,
        team_id: str,
        assignee_id: Optional[str] = None,
        priority: int = 0,
        due_date: Optional[str] = None,
    ) -> Optional[Dict]:
        """Create issue in Linear"""
        if not self.api_key:
            logger.warning("Linear API key not configured")
            return None
        
        mutation = """
        mutation CreateIssue($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue {
              id
              identifier
              title
              url
            }
          }
        }
        """
        
        variables = {
            "input": {
                "title": title,
                "description": description,
                "teamId": team_id,
            }
        }
        
        if assignee_id:
            variables["input"]["assigneeId"] = assignee_id
        if priority:
            variables["input"]["priority"] = str(priority)  # type: ignore
        if due_date:
            variables["input"]["dueDate"] = due_date
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    json={"query": mutation, "variables": variables},
                    headers={
                        "Authorization": self.api_key,
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("data", {}).get("issueCreate", {}).get("success"):
                    return data["data"]["issueCreate"]["issue"]
                else:
                    logger.error(f"Failed to create Linear issue: {data}")
                    return None
            except httpx.HTTPError as e:
                logger.error(f"Linear API error: {e}")
                return None
    
    async def update_issue_status(
        self,
        issue_id: str,
        state_id: str,
    ) -> bool:
        """Update issue status"""
        if not self.api_key:
            return False
        
        mutation = """
        mutation UpdateIssue($id: String!, $stateId: String!) {
          issueUpdate(id: $id, input: { stateId: $stateId }) {
            success
          }
        }
        """
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    json={
                        "query": mutation,
                        "variables": {"id": issue_id, "stateId": state_id},
                    },
                    headers={
                        "Authorization": self.api_key,
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data", {}).get("issueUpdate", {}).get("success", False)
            except httpx.HTTPError as e:
                logger.error(f"Failed to update Linear issue: {e}")
                return False
    
    async def get_teams(self) -> List[Dict]:
        """Get user's teams"""
        if not self.api_key:
            return []
        
        query = """
        query {
          teams {
            nodes {
              id
              name
              key
            }
          }
        }
        """
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    json={"query": query},
                    headers={
                        "Authorization": self.api_key,
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data", {}).get("teams", {}).get("nodes", [])
            except httpx.HTTPError as e:
                logger.error(f"Failed to get Linear teams: {e}")
                return []


# Global instance
linear_service = LinearService()
