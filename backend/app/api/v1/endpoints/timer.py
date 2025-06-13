"""Focus timer endpoints."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func

from app.auth.dependencies import get_current_user
from app.models.database import get_db
from app.models.models import User, Activity, Project
from app.schemas.schemas import TimerSession, TimerSessionResponse, Activity as ActivitySchema

router = APIRouter()

# In-memory storage for active timer sessions
# In production, this should be Redis or similar
active_sessions: Dict[str, dict] = {}


@router.post("/start", response_model=TimerSessionResponse)
async def start_timer_session(
    timer_session: TimerSession,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a new focus timer session."""
    session_id = uuid4()
    started_at = datetime.now()
    estimated_end = started_at + timedelta(minutes=timer_session.duration_minutes)
    
    # Validate project if specified
    if timer_session.project_id:
        project_stmt = select(Project).where(
            and_(
                Project.id == timer_session.project_id,
                Project.user_id == current_user.id
            )
        )
        project = (await db.execute(project_stmt)).scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    
    # Store session in memory
    session_data = {
        "session_id": session_id,
        "user_id": current_user.id,
        "project_id": timer_session.project_id,
        "activity_type": timer_session.activity_type,
        "description": timer_session.description,
        "duration_minutes": timer_session.duration_minutes,
        "tags": timer_session.tags,
        "started_at": started_at,
        "estimated_end": estimated_end,
        "is_active": True,
        "paused_duration": 0,
    }
    
    active_sessions[str(session_id)] = session_data
    
    return TimerSessionResponse(
        session_id=session_id,
        project_id=timer_session.project_id,
        activity_type=timer_session.activity_type,
        description=timer_session.description,
        duration_minutes=timer_session.duration_minutes,
        started_at=started_at,
        estimated_end=estimated_end,
        tags=timer_session.tags,
    )


@router.get("/session/{session_id}")
async def get_timer_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Get current timer session status."""
    session_data = active_sessions.get(str(session_id))
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer session not found"
        )
    
    if session_data["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    now = datetime.now()
    elapsed_minutes = (now - session_data["started_at"]).total_seconds() / 60
    remaining_minutes = max(0, session_data["duration_minutes"] - elapsed_minutes)
    
    return {
        "session_id": session_data["session_id"],
        "project_id": session_data["project_id"],
        "activity_type": session_data["activity_type"],
        "description": session_data["description"],
        "duration_minutes": session_data["duration_minutes"],
        "started_at": session_data["started_at"],
        "estimated_end": session_data["estimated_end"],
        "elapsed_minutes": int(elapsed_minutes),
        "remaining_minutes": int(remaining_minutes),
        "is_active": session_data["is_active"],
        "progress_percentage": min(100, (elapsed_minutes / session_data["duration_minutes"]) * 100),
        "tags": session_data["tags"],
    }


@router.post("/session/{session_id}/pause")
async def pause_timer_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Pause an active timer session."""
    session_data = active_sessions.get(str(session_id))
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer session not found"
        )
    
    if session_data["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if not session_data["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timer session is not active"
        )
    
    session_data["is_active"] = False
    session_data["paused_at"] = datetime.now()
    
    return {"message": "Timer session paused", "session_id": session_id}


@router.post("/session/{session_id}/resume")
async def resume_timer_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Resume a paused timer session."""
    session_data = active_sessions.get(str(session_id))
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer session not found"
        )
    
    if session_data["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if session_data["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timer session is already active"
        )
    
    # Calculate paused duration and adjust estimated end time
    now = datetime.now()
    paused_duration = (now - session_data["paused_at"]).total_seconds() / 60
    session_data["paused_duration"] += paused_duration
    session_data["estimated_end"] = session_data["estimated_end"] + timedelta(minutes=paused_duration)
    session_data["is_active"] = True
    
    if "paused_at" in session_data:
        del session_data["paused_at"]
    
    return {"message": "Timer session resumed", "session_id": session_id}


@router.post("/session/{session_id}/complete", response_model=ActivitySchema)
async def complete_timer_session(
    session_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Complete a timer session and create an activity record."""
    session_data = active_sessions.get(str(session_id))
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer session not found"
        )
    
    if session_data["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    now = datetime.now()
    actual_duration = (now - session_data["started_at"]).total_seconds() / 60
    actual_duration -= session_data["paused_duration"]
    actual_duration = max(1, int(actual_duration))  # Minimum 1 minute
    
    # Create activity record
    activity = Activity(
        user_id=current_user.id,
        project_id=session_data["project_id"],
        activity_type=session_data["activity_type"],
        description=session_data["description"] or f"Focus session - {session_data['activity_type']}",
        duration_minutes=actual_duration,
        started_at=session_data["started_at"],
        ended_at=now,
        tags=session_data["tags"] or []
    )
    
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    
    # Clean up session
    background_tasks.add_task(cleanup_session, str(session_id))
    
    return ActivitySchema.model_validate(activity)


@router.delete("/session/{session_id}")
async def cancel_timer_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Cancel an active timer session without creating an activity."""
    session_data = active_sessions.get(str(session_id))
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timer session not found"
        )
    
    if session_data["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Remove session
    del active_sessions[str(session_id)]
    
    return {"message": "Timer session cancelled", "session_id": session_id}


@router.get("/active")
async def get_active_sessions(
    current_user: User = Depends(get_current_user),
):
    """Get all active timer sessions for the current user."""
    user_sessions = []
    
    for session_id, session_data in active_sessions.items():
        if session_data["user_id"] == current_user.id:
            now = datetime.now()
            elapsed_minutes = (now - session_data["started_at"]).total_seconds() / 60
            remaining_minutes = max(0, session_data["duration_minutes"] - elapsed_minutes)
            
            user_sessions.append({
                "session_id": session_data["session_id"],
                "project_id": session_data["project_id"],
                "activity_type": session_data["activity_type"],
                "description": session_data["description"],
                "duration_minutes": session_data["duration_minutes"],
                "started_at": session_data["started_at"],
                "elapsed_minutes": int(elapsed_minutes),
                "remaining_minutes": int(remaining_minutes),
                "is_active": session_data["is_active"],
                "progress_percentage": min(100, (elapsed_minutes / session_data["duration_minutes"]) * 100),
            })
    
    return {"active_sessions": user_sessions}


@router.get("/history")
async def get_timer_history(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get timer session history (completed activities)."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get activities that were created through timer sessions
    # We can identify these by looking for activities with tags containing "timer" or similar
    activities_stmt = select(Activity).where(
        and_(
            Activity.user_id == current_user.id,
            Activity.created_at >= start_date,
            Activity.created_at <= end_date
        )
    ).order_by(Activity.created_at.desc())
    
    activities = (await db.execute(activities_stmt)).scalars().all()
    
    # Get daily summary
    daily_summary = {}
    total_sessions = 0
    total_minutes = 0
    
    for activity in activities:
        date_key = activity.created_at.date().isoformat()
        
        if date_key not in daily_summary:
            daily_summary[date_key] = {
                "date": activity.created_at.date(),
                "sessions": 0,
                "total_minutes": 0,
                "activity_types": {}
            }
        
        daily_summary[date_key]["sessions"] += 1
        daily_summary[date_key]["total_minutes"] += activity.duration_minutes
        
        activity_type = activity.activity_type
        if activity_type not in daily_summary[date_key]["activity_types"]:
            daily_summary[date_key]["activity_types"][activity_type] = 0
        daily_summary[date_key]["activity_types"][activity_type] += activity.duration_minutes
        
        total_sessions += 1
        total_minutes += activity.duration_minutes
    
    return {
        "daily_summary": list(daily_summary.values()),
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "avg_session_length": total_minutes / total_sessions if total_sessions > 0 else 0,
        "recent_activities": [ActivitySchema.model_validate(activity) for activity in activities[:10]]
    }


def cleanup_session(session_id: str):
    """Background task to clean up completed sessions."""
    if session_id in active_sessions:
        del active_sessions[session_id]
