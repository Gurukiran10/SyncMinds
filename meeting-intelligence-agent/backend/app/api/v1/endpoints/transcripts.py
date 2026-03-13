"""
Transcripts API Endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_transcripts():
    """List transcripts - implementation placeholder"""
    return {"message": "Transcripts endpoint"}
