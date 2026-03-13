"""
Zoom Integration Service
"""
import logging
from typing import Dict, Optional, List
import httpx
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class ZoomService:
    """Service for Zoom integration"""
    
    def __init__(self):
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        self.bot_jwt = settings.ZOOM_BOT_JWT
        self.base_url = "https://api.zoom.us/v2"
    
    async def get_meeting_details(self, meeting_id: str) -> Optional[Dict]:
        """Get meeting details from Zoom"""
        if not self.bot_jwt:
            logger.warning("Zoom JWT not configured")
            return None
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/meetings/{meeting_id}",
                    headers={
                        "Authorization": f"Bearer {self.bot_jwt}",
                    },
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to get Zoom meeting: {e}")
                return None
    
    async def add_bot_to_meeting(self, meeting_id: str) -> Dict:
        """
        Add bot to Zoom meeting to record and transcribe
        
        Note: Requires Zoom App Marketplace app with Meeting SDK
        This is a placeholder for the actual SDK integration
        """
        logger.info(f"Adding bot to meeting: {meeting_id}")
        
        # In production, this would:
        # 1. Use Zoom Meeting SDK to join meeting
        # 2. Start video/audio capture
        # 3. Stream to transcription service
        # 4. Handle recording storage
        
        return {
            "meeting_id": meeting_id,
            "bot_joined": True,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def list_upcoming_meetings(
        self,
        user_id: str,
        from_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """List upcoming meetings for user"""
        if not self.bot_jwt:
            return []
        
        async with httpx.AsyncClient() as client:
            try:
                params = {"type": "upcoming"}
                if from_date:
                    params["from"] = from_date.strftime("%Y-%m-%d")
                
                response = await client.get(
                    f"{self.base_url}/users/{user_id}/meetings",
                    headers={"Authorization": f"Bearer {self.bot_jwt}"},
                    params=params,
                )
                response.raise_for_status()
                return response.json().get("meetings", [])
            except httpx.HTTPError as e:
                logger.error(f"Failed to list meetings: {e}")
                return []
    
    async def get_meeting_recording(self, meeting_id: str) -> Optional[Dict]:
        """Get meeting recording details"""
        if not self.bot_jwt:
            return None
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/meetings/{meeting_id}/recordings",
                    headers={"Authorization": f"Bearer {self.bot_jwt}"},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to get recording: {e}")
                return None
    
    async def download_recording(self, download_url: str, output_path: str) -> str:
        """Download meeting recording"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    download_url,
                    headers={"Authorization": f"Bearer {self.bot_jwt}"},
                )
                response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                return output_path
            except httpx.HTTPError as e:
                logger.error(f"Failed to download recording: {e}")
                raise


# Global instance
zoom_service = ZoomService()
