"""
Knowledge API Endpoints — semantic search, recurring topics, cross-meeting graph.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.meeting import Meeting
from app.models.user import User
from app.services.knowledge.embeddings import (
    get_recurring_topics,
    semantic_search,
)

router = APIRouter()


@router.get("/search")
async def search_knowledge(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Semantic search across all meetings the user has access to.
    Falls back to keyword search when embeddings are unavailable.
    """
    results = semantic_search(query=q, db=db, user=current_user, limit=limit)
    return {"query": q, "results": results, "total": len(results)}


@router.get("/topics")
async def list_recurring_topics(
    min_count: int = Query(2, ge=2, description="Minimum meetings a topic must appear in"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return topics that appear across multiple meetings."""
    topics = get_recurring_topics(db=db, user=current_user, min_count=min_count)
    return {"topics": topics, "total": len(topics)}


@router.get("/graph")
async def get_meeting_graph(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return meetings related to the given meeting, based on:
    - Shared attendees (weight 1 per shared attendee)
    - Overlapping discussion topics (weight 2 per shared topic)
    """
    user_id = str(current_user.id)

    anchor = db.execute(
        select(Meeting).where(Meeting.id == meeting_id)
    ).scalar_one_or_none()
    if not anchor:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    # Access check
    anchor_attendees = set(str(aid) for aid in (anchor.attendee_ids or []))
    if str(anchor.organizer_id) != user_id and user_id not in anchor_attendees:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    anchor_topics = set(str(t).lower() for t in (anchor.discussion_topics or []))

    all_meetings = db.execute(select(Meeting)).scalars().all()

    edges = []
    for meeting in all_meetings:
        if str(meeting.id) == meeting_id:
            continue

        # Access check for related meeting
        m_attendees = set(str(aid) for aid in (meeting.attendee_ids or []))
        if str(meeting.organizer_id) != user_id and user_id not in m_attendees:
            continue

        weight = 0
        shared_attendees = list(anchor_attendees & m_attendees)
        shared_topics = list(anchor_topics & set(str(t).lower() for t in (meeting.discussion_topics or [])))

        weight += len(shared_attendees)
        weight += len(shared_topics) * 2

        if weight > 0:
            edges.append({
                "meeting_id": str(meeting.id),
                "meeting_title": meeting.title,
                "meeting_date": meeting.scheduled_start.isoformat() if meeting.scheduled_start else None,
                "weight": weight,
                "shared_attendee_count": len(shared_attendees),
                "shared_topics": shared_topics,
            })

    edges.sort(key=lambda e: e["weight"], reverse=True)

    return {
        "anchor_meeting_id": meeting_id,
        "anchor_title": anchor.title,
        "related_meetings": edges[:20],
        "total": len(edges),
    }
