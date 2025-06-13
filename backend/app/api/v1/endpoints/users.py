"""User management endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.models.database import get_db
from app.models.models import User as UserModel
from app.schemas.schemas import User, UserUpdate, MessageResponse

router = APIRouter()


@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: UserModel = Depends(get_current_user),
) -> User:
    """Get current user profile."""
    return User.model_validate(current_user)


@router.put("/me", response_model=User)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update current user profile."""
    # Update user fields
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return User.model_validate(current_user)


@router.delete("/me", response_model=MessageResponse)
async def delete_current_user_account(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete current user account."""
    await db.delete(current_user)
    await db.commit()
    
    return MessageResponse(message="Account deleted successfully")


@router.get("/me/stats")
async def get_user_stats(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user statistics summary."""
    # Get user stats
    stmt = select(UserModel).options(
        selectinload(UserModel.activities),
        selectinload(UserModel.moods),
        selectinload(UserModel.projects),
    ).where(UserModel.id == current_user.id)
    
    result = await db.execute(stmt)
    user_with_relations = result.scalar_one()
    
    total_activities = len(user_with_relations.activities)
    total_moods = len(user_with_relations.moods)
    total_projects = len(user_with_relations.projects)
    active_projects = len([p for p in user_with_relations.projects if p.is_active])
    
    total_minutes = sum(activity.duration_minutes for activity in user_with_relations.activities)
    
    # Calculate average mood if moods exist
    avg_mood = None
    avg_energy = None
    avg_stress = None
    
    if user_with_relations.moods:
        avg_mood = sum(mood.mood_score for mood in user_with_relations.moods) / len(user_with_relations.moods)
        avg_energy = sum(mood.energy_level for mood in user_with_relations.moods) / len(user_with_relations.moods)
        avg_stress = sum(mood.stress_level for mood in user_with_relations.moods) / len(user_with_relations.moods)
    
    return {
        "total_activities": total_activities,
        "total_moods": total_moods,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_minutes_tracked": total_minutes,
        "avg_mood_score": round(avg_mood, 2) if avg_mood else None,
        "avg_energy_level": round(avg_energy, 2) if avg_energy else None,
        "avg_stress_level": round(avg_stress, 2) if avg_stress else None,
        "member_since": current_user.created_at,
        "last_activity": max(
            (activity.created_at for activity in user_with_relations.activities), 
            default=None
        ),
    }
