"""
Decisions API Endpoints — outcome tracking for extracted meeting decisions.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.meeting import Meeting
from app.models.user import User

router = APIRouter()


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class DecisionResponse(BaseModel):
    index: int
    decision: str
    decision_maker: Optional[str]
    reasoning: Optional[str]
    alternatives: Optional[List[str]]
    reversibility: Optional[str]
    impact_level: Optional[str]
    actual_outcome: Optional[str]
    outcome_met_expectation: Optional[bool]
    implementation_status: Optional[str]
    implemented_at: Optional[str]


class DecisionOutcomeUpdate(BaseModel):
    actual_outcome: Optional[str] = None
    outcome_met_expectation: Optional[bool] = None
    implementation_status: Optional[str] = None  # "pending" | "in_progress" | "done" | "abandoned"
    implemented_at: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_meeting_or_404(db: Session, meeting_id: str, user: User) -> Meeting:
    meeting = db.execute(
        select(Meeting).where(Meeting.id == meeting_id)
    ).scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    # Allow access if user is organizer or attendee
    attendee_ids = [str(aid) for aid in (meeting.attendee_ids or [])]
    if str(meeting.organizer_id) != str(user.id) and str(user.id) not in attendee_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return meeting


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/meetings/{meeting_id}/decisions", response_model=List[DecisionResponse])
async def list_meeting_decisions(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all decisions extracted from a meeting."""
    meeting = _get_meeting_or_404(db, meeting_id, current_user)
    raw_decisions: List[Dict[str, Any]] = meeting.key_decisions or []  # type: ignore[assignment]

    result = []
    for idx, d in enumerate(raw_decisions):
        result.append(
            DecisionResponse(
                index=idx,
                decision=d.get("decision", ""),
                decision_maker=d.get("decision_maker"),
                reasoning=d.get("reasoning"),
                alternatives=d.get("alternatives"),
                reversibility=d.get("reversibility"),
                impact_level=d.get("impact_level"),
                actual_outcome=d.get("actual_outcome"),
                outcome_met_expectation=d.get("outcome_met_expectation"),
                implementation_status=d.get("implementation_status", "pending"),
                implemented_at=d.get("implemented_at"),
            )
        )
    return result


@router.patch("/meetings/{meeting_id}/decisions/{decision_index}", response_model=DecisionResponse)
async def update_decision_outcome(
    meeting_id: str,
    decision_index: int,
    update: DecisionOutcomeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the outcome tracking fields for a specific decision."""
    meeting = _get_meeting_or_404(db, meeting_id, current_user)
    decisions: List[Dict[str, Any]] = list(meeting.key_decisions or [])  # type: ignore[assignment]

    if decision_index < 0 or decision_index >= len(decisions):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision index {decision_index} not found",
        )

    decision = dict(decisions[decision_index])

    if update.actual_outcome is not None:
        decision["actual_outcome"] = update.actual_outcome
    if update.outcome_met_expectation is not None:
        decision["outcome_met_expectation"] = update.outcome_met_expectation
    if update.implementation_status is not None:
        decision["implementation_status"] = update.implementation_status
    if update.implemented_at is not None:
        decision["implemented_at"] = update.implemented_at
    elif update.implementation_status == "done" and not decision.get("implemented_at"):
        decision["implemented_at"] = datetime.utcnow().isoformat()

    decisions[decision_index] = decision
    meeting.key_decisions = decisions  # type: ignore[assignment]
    db.commit()

    return DecisionResponse(
        index=decision_index,
        decision=decision.get("decision", ""),
        decision_maker=decision.get("decision_maker"),
        reasoning=decision.get("reasoning"),
        alternatives=decision.get("alternatives"),
        reversibility=decision.get("reversibility"),
        impact_level=decision.get("impact_level"),
        actual_outcome=decision.get("actual_outcome"),
        outcome_met_expectation=decision.get("outcome_met_expectation"),
        implementation_status=decision.get("implementation_status", "pending"),
        implemented_at=decision.get("implemented_at"),
    )


@router.get("/decisions/pending")
async def list_pending_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List decisions across all user's meetings that are not yet implemented."""
    # Get all meetings where user is organizer or attendee
    all_meetings = db.execute(select(Meeting)).scalars().all()
    user_id = str(current_user.id)

    pending = []
    for meeting in all_meetings:
        attendee_ids = [str(aid) for aid in (meeting.attendee_ids or [])]
        if str(meeting.organizer_id) != user_id and user_id not in attendee_ids:
            continue

        for idx, d in enumerate(meeting.key_decisions or []):  # type: ignore[union-attr]
            status_val = d.get("implementation_status", "pending")
            if status_val not in ("done", "abandoned"):
                pending.append({
                    "meeting_id": str(meeting.id),
                    "meeting_title": meeting.title,
                    "meeting_date": meeting.scheduled_start.isoformat() if meeting.scheduled_start else None,
                    "decision_index": idx,
                    "decision": d.get("decision"),
                    "decision_maker": d.get("decision_maker"),
                    "implementation_status": status_val,
                })

    return {"decisions": pending, "total": len(pending)}
