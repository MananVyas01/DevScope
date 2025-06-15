"""Analytics and statistics endpoints."""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.dependencies import get_current_user
from app.models.database import get_db
from app.models.models import User, Activity, Mood, Project, ProjectStats
from app.schemas.schemas import DailyStats, WeeklyStats, MonthlyStats

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard analytics summary."""
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Today's stats
    today_activities_stmt = select(Activity).where(
        and_(
            Activity.user_id == current_user.id, func.date(Activity.created_at) == today
        )
    )
    today_activities = (await db.execute(today_activities_stmt)).scalars().all()

    # Week's stats
    week_activities_stmt = select(Activity).where(
        and_(
            Activity.user_id == current_user.id,
            func.date(Activity.created_at) >= week_start,
        )
    )
    week_activities = (await db.execute(week_activities_stmt)).scalars().all()

    # Month's stats
    month_activities_stmt = select(Activity).where(
        and_(
            Activity.user_id == current_user.id,
            func.date(Activity.created_at) >= month_start,
        )
    )
    month_activities = (await db.execute(month_activities_stmt)).scalars().all()

    # Recent mood
    recent_mood_stmt = (
        select(Mood)
        .where(Mood.user_id == current_user.id)
        .order_by(Mood.created_at.desc())
        .limit(1)
    )
    recent_mood = (await db.execute(recent_mood_stmt)).scalar_one_or_none()

    # Active projects count
    active_projects_stmt = select(func.count(Project.id)).where(
        and_(Project.user_id == current_user.id, Project.is_active == True)
    )
    active_projects_count = (await db.execute(active_projects_stmt)).scalar()

    return {
        "today": {
            "minutes": sum(a.duration_minutes for a in today_activities),
            "activities": len(today_activities),
            "activity_breakdown": _get_activity_breakdown(today_activities),
        },
        "week": {
            "minutes": sum(a.duration_minutes for a in week_activities),
            "activities": len(week_activities),
            "activity_breakdown": _get_activity_breakdown(week_activities),
        },
        "month": {
            "minutes": sum(a.duration_minutes for a in month_activities),
            "activities": len(month_activities),
            "activity_breakdown": _get_activity_breakdown(month_activities),
        },
        "recent_mood": {
            "score": recent_mood.mood_score if recent_mood else None,
            "energy": recent_mood.energy_level if recent_mood else None,
            "stress": recent_mood.stress_level if recent_mood else None,
            "created_at": recent_mood.created_at if recent_mood else None,
        },
        "active_projects": active_projects_count,
    }


@router.get("/daily")
async def get_daily_analytics(
    days: int = Query(default=7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get daily analytics for the specified number of days."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)

    # Get activities for the date range
    activities_stmt = (
        select(Activity)
        .where(
            and_(
                Activity.user_id == current_user.id,
                func.date(Activity.created_at) >= start_date,
                func.date(Activity.created_at) <= end_date,
            )
        )
        .order_by(Activity.created_at)
    )

    activities = (await db.execute(activities_stmt)).scalars().all()

    # Get moods for the date range
    moods_stmt = (
        select(Mood)
        .where(
            and_(
                Mood.user_id == current_user.id,
                func.date(Mood.created_at) >= start_date,
                func.date(Mood.created_at) <= end_date,
            )
        )
        .order_by(Mood.created_at)
    )

    moods = (await db.execute(moods_stmt)).scalars().all()

    # Group by date
    daily_data = {}
    current_date = start_date

    while current_date <= end_date:
        day_activities = [a for a in activities if a.created_at.date() == current_date]
        day_moods = [m for m in moods if m.created_at.date() == current_date]

        daily_data[current_date.isoformat()] = {
            "date": current_date,
            "total_minutes": sum(a.duration_minutes for a in day_activities),
            "activities_count": len(day_activities),
            "activity_breakdown": _get_activity_breakdown(day_activities),
            "avg_mood_score": _get_avg_mood(day_moods, "mood_score"),
            "avg_energy_level": _get_avg_mood(day_moods, "energy_level"),
            "avg_stress_level": _get_avg_mood(day_moods, "stress_level"),
        }

        current_date += timedelta(days=1)

    return {"daily_stats": list(daily_data.values())}


@router.get("/productivity-trends")
async def get_productivity_trends(
    days: int = Query(default=30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get productivity trends over time."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)

    # Get activities grouped by date
    activities_stmt = (
        select(
            func.date(Activity.created_at).label("date"),
            func.sum(Activity.duration_minutes).label("total_minutes"),
            func.count(Activity.id).label("activity_count"),
            Activity.activity_type,
        )
        .where(
            and_(
                Activity.user_id == current_user.id,
                func.date(Activity.created_at) >= start_date,
                func.date(Activity.created_at) <= end_date,
            )
        )
        .group_by(func.date(Activity.created_at), Activity.activity_type)
        .order_by(func.date(Activity.created_at))
    )

    result = await db.execute(activities_stmt)
    activity_data = result.all()

    # Get mood trends
    moods_stmt = (
        select(
            func.date(Mood.created_at).label("date"),
            func.avg(Mood.mood_score).label("avg_mood"),
            func.avg(Mood.energy_level).label("avg_energy"),
            func.avg(Mood.stress_level).label("avg_stress"),
        )
        .where(
            and_(
                Mood.user_id == current_user.id,
                func.date(Mood.created_at) >= start_date,
                func.date(Mood.created_at) <= end_date,
            )
        )
        .group_by(func.date(Mood.created_at))
        .order_by(func.date(Mood.created_at))
    )

    mood_result = await db.execute(moods_stmt)
    mood_data = mood_result.all()

    # Process data for charts
    productivity_data = []
    mood_trends = []

    # Group activity data by date
    activity_by_date = {}
    for row in activity_data:
        date_str = row.date.isoformat()
        if date_str not in activity_by_date:
            activity_by_date[date_str] = {}
        activity_by_date[date_str][row.activity_type] = {
            "minutes": row.total_minutes,
            "count": row.activity_count,
        }

    # Create productivity trend
    for date_str, activities in activity_by_date.items():
        total_minutes = sum(act["minutes"] for act in activities.values())
        productivity_data.append(
            {
                "date": date_str,
                "total_minutes": total_minutes,
                "activity_breakdown": activities,
            }
        )

    # Create mood trend
    for row in mood_data:
        mood_trends.append(
            {
                "date": row.date.isoformat(),
                "avg_mood": round(float(row.avg_mood), 2),
                "avg_energy": round(float(row.avg_energy), 2),
                "avg_stress": round(float(row.avg_stress), 2),
            }
        )

    return {
        "productivity_trends": productivity_data,
        "mood_trends": mood_trends,
        "summary": {
            "total_days": days,
            "avg_daily_minutes": (
                sum(p["total_minutes"] for p in productivity_data) / days
                if productivity_data
                else 0
            ),
            "most_productive_day": (
                max(productivity_data, key=lambda x: x["total_minutes"])["date"]
                if productivity_data
                else None
            ),
        },
    }


@router.get("/project-breakdown")
async def get_project_breakdown(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get project time breakdown."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)

    # Get project time breakdown
    stmt = (
        select(
            Project.id,
            Project.name,
            Project.color,
            func.sum(Activity.duration_minutes).label("total_minutes"),
            func.count(Activity.id).label("activity_count"),
        )
        .join(Activity, Activity.project_id == Project.id)
        .where(
            and_(
                Project.user_id == current_user.id,
                func.date(Activity.created_at) >= start_date,
                func.date(Activity.created_at) <= end_date,
            )
        )
        .group_by(Project.id, Project.name, Project.color)
        .order_by(func.sum(Activity.duration_minutes).desc())
    )

    result = await db.execute(stmt)
    project_data = result.all()

    # Get activities without project
    no_project_stmt = select(
        func.sum(Activity.duration_minutes).label("total_minutes"),
        func.count(Activity.id).label("activity_count"),
    ).where(
        and_(
            Activity.user_id == current_user.id,
            Activity.project_id.is_(None),
            func.date(Activity.created_at) >= start_date,
            func.date(Activity.created_at) <= end_date,
        )
    )

    no_project_result = await db.execute(no_project_stmt)
    no_project_data = no_project_result.first()

    projects = []
    total_minutes = 0

    for row in project_data:
        minutes = int(row.total_minutes)
        projects.append(
            {
                "id": str(row.id),
                "name": row.name,
                "color": row.color,
                "minutes": minutes,
                "activity_count": row.activity_count,
            }
        )
        total_minutes += minutes

    # Add unassigned time
    if no_project_data and no_project_data.total_minutes:
        unassigned_minutes = int(no_project_data.total_minutes)
        projects.append(
            {
                "id": None,
                "name": "Unassigned",
                "color": "#6B7280",
                "minutes": unassigned_minutes,
                "activity_count": no_project_data.activity_count,
            }
        )
        total_minutes += unassigned_minutes

    # Calculate percentages
    for project in projects:
        project["percentage"] = (
            round((project["minutes"] / total_minutes * 100), 1)
            if total_minutes > 0
            else 0
        )

    return {
        "projects": projects,
        "total_minutes": total_minutes,
        "total_projects": len([p for p in projects if p["id"] is not None]),
    }


def _get_activity_breakdown(activities: List[Activity]) -> dict:
    """Get activity type breakdown."""
    breakdown = {}
    for activity in activities:
        activity_type = activity.activity_type
        if activity_type not in breakdown:
            breakdown[activity_type] = 0
        breakdown[activity_type] += activity.duration_minutes
    return breakdown


def _get_avg_mood(moods: List[Mood], field: str) -> Optional[float]:
    """Calculate average mood field."""
    if not moods:
        return None

    values = [getattr(mood, field) for mood in moods]
    return round(sum(values) / len(values), 2)
