"""Mentions API Endpoints"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.mention import Mention
from app.models.user import User

router = APIRouter()


class MentionResponse(BaseModel):
    id: UUID
    meeting_id: UUID
    user_id: UUID
    mention_type: str
    mentioned_text: str
    relevance_score: Optional[float]
    urgency_score: Optional[float]
    sentiment: Optional[str]
    notification_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[MentionResponse])
async def list_mentions(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List mentions for current user"""
    query = select(Mention).where(Mention.user_id == current_user.id)
    if unread_only:
        query = query.where(Mention.notification_read.is_(False))

    query = query.order_by(desc(Mention.created_at)).offset(skip).limit(limit)
    result = db.execute(query)
    return result.scalars().all()


@router.get("/{mention_id}", response_model=MentionResponse)
async def get_mention(
    mention_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get single mention"""
    result = db.execute(
        select(Mention).where(
            Mention.id == mention_id,
            Mention.user_id == current_user.id,
        )
    )
    mention = result.scalar_one_or_none()
    if not mention:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mention not found")
    return mention


@router.post("/{mention_id}/read", response_model=MentionResponse)
async def mark_mention_read(
    mention_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark mention as read"""
    result = db.execute(
        select(Mention).where(
            Mention.id == mention_id,
            Mention.user_id == current_user.id,
        )
    )
    mention = result.scalar_one_or_none()
    if not mention:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mention not found")

    mention.notification_read = True  # type: ignore
    mention.notification_read_at = datetime.utcnow()  # type: ignore
    db.commit()
    db.refresh(mention)
    return mention
