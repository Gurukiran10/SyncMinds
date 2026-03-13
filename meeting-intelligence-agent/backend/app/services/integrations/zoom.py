"""
Zoom Integration Service
Uses Server-to-Server OAuth (replaces deprecated JWT).
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_token_cache: Dict[str, object] = {}  # {"token": str, "expires_at": datetime}


class ZoomService:
    """Service for Zoom integration using Server-to-Server OAuth."""

    BASE_URL = "https://api.zoom.us/v2"
    TOKEN_URL = "https://zoom.us/oauth/token"

    def __init__(self):
        self.account_id = settings.ZOOM_CLIENT_ID       # reuse field as account_id
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET

    def _is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    async def get_access_token(self) -> Optional[str]:
        """
        Exchange client credentials for a Server-to-Server OAuth access token.
        Tokens are cached until 60 seconds before expiry.
        """
        global _token_cache
        now = datetime.utcnow()
        if _token_cache.get("token") and isinstance(_token_cache.get("expires_at"), datetime):
            if now < _token_cache["expires_at"]:  # type: ignore[operator]
                return str(_token_cache["token"])

        if not self._is_configured():
            logger.warning("Zoom client credentials not configured")
            return None

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.post(
                    self.TOKEN_URL,
                    params={"grant_type": "account_credentials", "account_id": self.account_id},
                    auth=(self.client_id, self.client_secret),
                )
                resp.raise_for_status()
                data = resp.json()
                token = data["access_token"]
                expires_in = int(data.get("expires_in", 3600))
                _token_cache["token"] = token
                _token_cache["expires_at"] = now + timedelta(seconds=expires_in - 60)
                return token
            except Exception as e:
                logger.error(f"Failed to get Zoom access token: {e}")
                return None

    async def _headers(self) -> Optional[Dict[str, str]]:
        token = await self.get_access_token()
        if not token:
            return None
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async def get_meeting_details(self, meeting_id: str) -> Optional[Dict]:
        """Get meeting details from Zoom."""
        headers = await self._headers()
        if not headers:
            return None

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(f"{self.BASE_URL}/meetings/{meeting_id}", headers=headers)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to get Zoom meeting {meeting_id}: {e}")
                return None

    async def add_bot_to_meeting(self, meeting_id: str, consent_given: bool = False) -> Dict:
        """
        Request cloud recording for a Zoom meeting via REST API.
        Full in-meeting bot requires Zoom Meeting SDK (native app).
        This REST approach starts cloud recording if the host is present.
        """
        if not consent_given:
            logger.warning(f"Consent not given for meeting {meeting_id} — skipping bot join")
            return {"meeting_id": meeting_id, "bot_joined": False, "reason": "consent_required"}

        headers = await self._headers()
        if not headers:
            return {"meeting_id": meeting_id, "bot_joined": False, "reason": "not_configured"}

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.patch(
                    f"{self.BASE_URL}/meetings/{meeting_id}/recordings/status",
                    headers=headers,
                    json={"action": "resume"},
                )
                if resp.status_code in (200, 204):
                    logger.info(f"Cloud recording started for Zoom meeting {meeting_id}")
                    return {"meeting_id": meeting_id, "bot_joined": True, "timestamp": datetime.utcnow().isoformat()}
                else:
                    logger.warning(f"Cloud recording start returned {resp.status_code} for {meeting_id}")
                    return {"meeting_id": meeting_id, "bot_joined": False, "reason": f"status_{resp.status_code}"}
            except httpx.HTTPError as e:
                logger.error(f"Failed to start cloud recording for meeting {meeting_id}: {e}")
                return {"meeting_id": meeting_id, "bot_joined": False, "reason": str(e)}

    async def list_upcoming_meetings(
        self,
        user_id: str = "me",
        from_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """List upcoming meetings for a user."""
        headers = await self._headers()
        if not headers:
            return []

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                params: Dict = {"type": "upcoming"}
                if from_date:
                    params["from"] = from_date.strftime("%Y-%m-%d")

                resp = await client.get(
                    f"{self.BASE_URL}/users/{user_id}/meetings",
                    headers=headers,
                    params=params,
                )
                resp.raise_for_status()
                return resp.json().get("meetings", [])
            except httpx.HTTPError as e:
                logger.error(f"Failed to list Zoom meetings: {e}")
                return []

    async def get_meeting_recording(self, meeting_id: str) -> Optional[Dict]:
        """Get recording details for a completed meeting."""
        headers = await self._headers()
        if not headers:
            return None

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/meetings/{meeting_id}/recordings",
                    headers=headers,
                )
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to get Zoom recording: {e}")
                return None

    async def download_recording(self, download_url: str, output_path: str) -> str:
        """Download a Zoom cloud recording file."""
        token = await self.get_access_token()
        params = {"access_token": token} if token else {}

        async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
            try:
                async with client.stream("GET", download_url, params=params) as resp:
                    resp.raise_for_status()
                    with open(output_path, "wb") as f:
                        async for chunk in resp.aiter_bytes(chunk_size=8192):
                            f.write(chunk)
                return output_path
            except httpx.HTTPError as e:
                logger.error(f"Failed to download Zoom recording: {e}")
                raise

    async def test_connection(self) -> bool:
        """Verify Zoom credentials are valid."""
        token = await self.get_access_token()
        return token is not None


# Global instance
zoom_service = ZoomService()
