"""VSCode extension integration endpoints."""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_optional
from app.models.database import get_db
from app.models.models import User, Activity, Project
from sqlalchemy.future import select

logger = logging.getLogger(__name__)
router = APIRouter()


class VSCodeActivityPayload(BaseModel):
    """VSCode activity session data."""

    sessionId: str
    startTime: str  # ISO format
    endTime: str  # ISO format
    filesEdited: List[str]
    keystrokes: int
    focusTime: int  # seconds
    idleTime: int  # seconds
    language: Optional[str] = None
    project: Optional[str] = None
    gitRepo: Optional[str] = None
    gitBranch: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class VSCodeSyncResponse(BaseModel):
    """Response for activity sync."""

    success: bool
    message: str
    activityId: Optional[int] = None
    sessionId: str


@router.post("/activity", response_model=VSCodeSyncResponse)
async def sync_vscode_activity(
    payload: VSCodeActivityPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Sync VSCode activity session to DevScope."""
    try:
        # For now, we'll accept anonymous data if user is not authenticated
        # In production, you might want to require authentication
        if not current_user:
            # Could create a guest/anonymous tracking system
            # For now, just log and return success
            logger.info(f"Anonymous VSCode activity: {payload.sessionId}")
            return VSCodeSyncResponse(
                success=True,
                message="Activity logged (anonymous)",
                sessionId=payload.sessionId,
            )

        # Parse timestamps
        try:
            start_time = datetime.fromisoformat(
                payload.startTime.replace("Z", "+00:00")
            )
            end_time = datetime.fromisoformat(payload.endTime.replace("Z", "+00:00"))
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid timestamp format: {e}",
            )

        # Calculate session duration
        session_duration = int(
            (end_time - start_time).total_seconds() / 60
        )  # Convert to minutes

        # Find or create project
        project = None
        if payload.project or payload.gitRepo:
            project_name = payload.project or payload.gitRepo
            # Look for existing project
            stmt = select(Project).where(
                Project.user_id == current_user.id, Project.name == project_name
            )
            result = await db.execute(stmt)
            project = result.scalar_one_or_none()

            if not project:
                # Create new project
                project = Project(
                    user_id=current_user.id,
                    name=project_name,
                    description=f"VSCode project: {project_name}",
                    github_repo=payload.gitRepo,
                    color="#007ACC",  # VSCode blue
                )
                db.add(project)
                await db.commit()
                await db.refresh(project)

        # Create activity
        activity_description = (
            f"VSCode session: {len(payload.filesEdited)} files edited"
        )
        if payload.language:
            activity_description += f" ({payload.language})"

        # Determine activity type based on session characteristics
        activity_type = "coding"
        if payload.focusTime < 60:  # Less than 1 minute of focus
            activity_type = "planning"
        elif len(payload.filesEdited) == 0:
            activity_type = "reading"

        # Build tags
        tags = ["vscode", "session"]
        if payload.language:
            tags.append(payload.language)
        if payload.gitBranch:
            tags.append(f"branch:{payload.gitBranch}")

        # Prepare metadata
        activity_metadata = {
            "vscode_session_id": payload.sessionId,
            "files_edited": payload.filesEdited,
            "keystrokes": payload.keystrokes,
            "focus_time_seconds": payload.focusTime,
            "idle_time_seconds": payload.idleTime,
            "git_repository": payload.gitRepo,
            "git_branch": payload.gitBranch,
            "source": "vscode-extension",
            **(payload.metadata or {}),
        }

        activity = Activity(
            user_id=current_user.id,
            project_id=project.id if project else None,
            activity_type=activity_type,
            description=activity_description,
            duration_minutes=max(session_duration, 1),  # At least 1 minute
            started_at=start_time,
            ended_at=end_time,
            tags=tags,
            metadata=activity_metadata,
        )

        db.add(activity)
        await db.commit()
        await db.refresh(activity)

        logger.info(f"VSCode activity synced: {activity.id} for user {current_user.id}")

        return VSCodeSyncResponse(
            success=True,
            message="Activity synced successfully",
            activityId=activity.id,
            sessionId=payload.sessionId,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing VSCode activity: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync activity data",
        )


@router.get("/status")
async def vscode_extension_status():
    """Check VSCode extension API status."""
    return {
        "status": "active",
        "version": "1.0.0",
        "supported_features": [
            "activity_tracking",
            "git_integration",
            "project_detection",
            "language_detection",
        ],
        "endpoints": {"sync_activity": "/vscode/activity", "status": "/vscode/status"},
    }


@router.get("/config")
async def get_vscode_config(
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get configuration for VSCode extension."""
    if not current_user:
        return {"configured": False, "message": "User not authenticated"}

    return {
        "configured": True,
        "user_id": current_user.id,
        "username": current_user.username,
        "github_username": current_user.github_username,
        "sync_interval": 300,  # 5 minutes
        "tracking_enabled": True,
        "features": {
            "git_integration": True,
            "ai_analysis": bool(current_user.github_username),
            "project_detection": True,
        },
    }
