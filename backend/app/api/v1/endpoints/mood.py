"""Mood tracking endpoints."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.dependencies import get_current_user
from app.models.database import get_db
from app.models.models import User, Mood as MoodModel
from app.schemas.schemas import Mood, MoodCreate, MoodUpdate, MessageResponse

router = APIRouter()


@router.post("/", response_model=Mood)
async def create_mood_entry(
    mood_data: MoodCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new mood entry."""
    mood = MoodModel(
        user_id=current_user.id,
        mood_score=mood_data.mood_score,
        energy_level=mood_data.energy_level,
        stress_level=mood_data.stress_level,
        notes=mood_data.notes,
        tags=mood_data.tags or []
    )
    
    db.add(mood)
    await db.commit()
    await db.refresh(mood)
    
    return Mood.model_validate(mood)


@router.get("/", response_model=List[Mood])
async def get_mood_entries(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get mood entries for the specified number of days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    stmt = select(MoodModel).where(
        and_(
            MoodModel.user_id == current_user.id,
            MoodModel.created_at >= start_date,
            MoodModel.created_at <= end_date
        )
    ).order_by(MoodModel.created_at.desc())
    
    moods = (await db.execute(stmt)).scalars().all()
    
    return [Mood.model_validate(mood) for mood in moods]


@router.get("/{mood_id}", response_model=Mood)
async def get_mood_entry(
    mood_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific mood entry."""
    stmt = select(MoodModel).where(
        and_(
            MoodModel.id == mood_id,
            MoodModel.user_id == current_user.id
        )
    )
    
    mood = (await db.execute(stmt)).scalar_one_or_none()
    
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood entry not found"
        )
    
    return Mood.model_validate(mood)


@router.put("/{mood_id}", response_model=Mood)
async def update_mood_entry(
    mood_id: UUID,
    mood_update: MoodUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a mood entry."""
    stmt = select(MoodModel).where(
        and_(
            MoodModel.id == mood_id,
            MoodModel.user_id == current_user.id
        )
    )
    
    mood = (await db.execute(stmt)).scalar_one_or_none()
    
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood entry not found"
        )
    
    # Update mood fields
    for field, value in mood_update.model_dump(exclude_unset=True).items():
        setattr(mood, field, value)
    
    db.add(mood)
    await db.commit()
    await db.refresh(mood)
    
    return Mood.model_validate(mood)


@router.delete("/{mood_id}", response_model=MessageResponse)
async def delete_mood_entry(
    mood_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a mood entry."""
    stmt = select(MoodModel).where(
        and_(
            MoodModel.id == mood_id,
            MoodModel.user_id == current_user.id
        )
    )
    
    mood = (await db.execute(stmt)).scalar_one_or_none()
    
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood entry not found"
        )
    
    await db.delete(mood)
    await db.commit()
    
    return MessageResponse(message="Mood entry deleted successfully")


@router.get("/analytics/trends")
async def get_mood_trends(
    days: int = Query(default=30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get mood trends and analytics."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get mood data for the period
    stmt = select(MoodModel).where(
        and_(
            MoodModel.user_id == current_user.id,
            MoodModel.created_at >= start_date,
            MoodModel.created_at <= end_date
        )
    ).order_by(MoodModel.created_at)
    
    moods = (await db.execute(stmt)).scalars().all()
    
    if not moods:
        return {
            "trends": [],
            "averages": None,
            "insights": [],
            "total_entries": 0
        }
    
    # Group by date for trends
    daily_trends = {}
    
    for mood in moods:
        date_key = mood.created_at.date()
        
        if date_key not in daily_trends:
            daily_trends[date_key] = {
                "date": date_key,
                "mood_scores": [],
                "energy_levels": [],
                "stress_levels": [],
                "entries": 0
            }
        
        daily_trends[date_key]["mood_scores"].append(mood.mood_score)
        daily_trends[date_key]["energy_levels"].append(mood.energy_level)
        daily_trends[date_key]["stress_levels"].append(mood.stress_level)
        daily_trends[date_key]["entries"] += 1
    
    # Calculate daily averages
    trends = []
    for date, data in sorted(daily_trends.items()):
        trends.append({
            "date": date.isoformat(),
            "avg_mood": round(sum(data["mood_scores"]) / len(data["mood_scores"]), 2),
            "avg_energy": round(sum(data["energy_levels"]) / len(data["energy_levels"]), 2),
            "avg_stress": round(sum(data["stress_levels"]) / len(data["stress_levels"]), 2),
            "entries": data["entries"]
        })
    
    # Calculate overall averages
    all_mood_scores = [mood.mood_score for mood in moods]
    all_energy_levels = [mood.energy_level for mood in moods]
    all_stress_levels = [mood.stress_level for mood in moods]
    
    averages = {
        "mood": round(sum(all_mood_scores) / len(all_mood_scores), 2),
        "energy": round(sum(all_energy_levels) / len(all_energy_levels), 2),
        "stress": round(sum(all_stress_levels) / len(all_stress_levels), 2)
    }
    
    # Generate insights
    insights = []
    
    # Mood trend analysis
    if len(trends) >= 7:
        recent_mood = sum(trend["avg_mood"] for trend in trends[-7:]) / 7
        earlier_mood = sum(trend["avg_mood"] for trend in trends[-14:-7]) / 7 if len(trends) >= 14 else recent_mood
        
        if recent_mood > earlier_mood + 0.5:
            insights.append("Your mood has been trending upward over the past week! 📈")
        elif recent_mood < earlier_mood - 0.5:
            insights.append("Your mood has been trending downward lately. Consider what might be affecting it. 📉")
        else:
            insights.append("Your mood has been relatively stable recently. 😊")
    
    # Energy level insights
    low_energy_days = sum(1 for trend in trends if trend["avg_energy"] <= 2)
    if low_energy_days > len(trends) * 0.3:  # More than 30% low energy days
        insights.append("You've had quite a few low-energy days. Make sure you're getting enough rest! ⚡")
    
    # Stress level insights
    high_stress_days = sum(1 for trend in trends if trend["avg_stress"] >= 4)
    if high_stress_days > len(trends) * 0.3:  # More than 30% high stress days
        insights.append("You've been experiencing high stress levels frequently. Consider stress management techniques. 🧘‍♀️")
    
    # Consistency insights
    if len(moods) < days * 0.5:  # Less than 50% tracking consistency
        insights.append("Try to log your mood more consistently for better insights! 📊")
    else:
        insights.append("Great job maintaining consistent mood tracking! 🎯")
    
    return {
        "trends": trends,
        "averages": averages,
        "insights": insights,
        "total_entries": len(moods),
        "tracking_consistency": round((len(moods) / days) * 100, 1)
    }


@router.get("/analytics/correlations")
async def get_mood_correlations(
    days: int = Query(default=30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get mood correlations with activities and productivity."""
    # Import Activity here to avoid circular imports
    from app.models.models import Activity
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get mood data
    mood_stmt = select(MoodModel).where(
        and_(
            MoodModel.user_id == current_user.id,
            MoodModel.created_at >= start_date,
            MoodModel.created_at <= end_date
        )
    ).order_by(MoodModel.created_at)
    
    moods = (await db.execute(mood_stmt)).scalars().all()
    
    # Get activity data for the same period
    activity_stmt = select(Activity).where(
        and_(
            Activity.user_id == current_user.id,
            Activity.created_at >= start_date,
            Activity.created_at <= end_date
        )
    ).order_by(Activity.created_at)
    
    activities = (await db.execute(activity_stmt)).scalars().all()
    
    if not moods or not activities:
        return {
            "correlations": {},
            "insights": ["Not enough data for correlation analysis. Keep tracking!"]
        }
    
    # Group data by date
    daily_data = {}
    
    # Add mood data
    for mood in moods:
        date_key = mood.created_at.date()
        if date_key not in daily_data:
            daily_data[date_key] = {
                "mood_scores": [],
                "energy_levels": [],
                "stress_levels": [],
                "total_minutes": 0,
                "activity_types": {}
            }
        
        daily_data[date_key]["mood_scores"].append(mood.mood_score)
        daily_data[date_key]["energy_levels"].append(mood.energy_level)
        daily_data[date_key]["stress_levels"].append(mood.stress_level)
    
    # Add activity data
    for activity in activities:
        date_key = activity.created_at.date()
        if date_key in daily_data:
            daily_data[date_key]["total_minutes"] += activity.duration_minutes
            
            activity_type = activity.activity_type
            if activity_type not in daily_data[date_key]["activity_types"]:
                daily_data[date_key]["activity_types"][activity_type] = 0
            daily_data[date_key]["activity_types"][activity_type] += activity.duration_minutes
    
    # Calculate correlations (simplified)
    correlations = {}
    insights = []
    
    # Productivity vs Mood correlation
    productive_days = []
    mood_scores = []
    
    for date, data in daily_data.items():
        if data["mood_scores"] and data["total_minutes"] > 0:
            avg_mood = sum(data["mood_scores"]) / len(data["mood_scores"])
            mood_scores.append(avg_mood)
            productive_days.append(data["total_minutes"])
    
    if len(mood_scores) >= 5:
        # Simple correlation calculation
        import statistics
        
        if len(set(productive_days)) > 1 and len(set(mood_scores)) > 1:
            try:
                correlation = statistics.correlation(mood_scores, productive_days)
                correlations["mood_productivity"] = round(correlation, 3)
                
                if correlation > 0.3:
                    insights.append("Higher mood scores correlate with more productive days! 🎯")
                elif correlation < -0.3:
                    insights.append("Interestingly, your mood doesn't seem to directly correlate with productivity.")
                else:
                    insights.append("Your mood and productivity show a mild correlation.")
            except statistics.StatisticsError:
                correlations["mood_productivity"] = 0
    
    # Activity type preferences by mood
    activity_mood_correlation = {}
    
    for date, data in daily_data.items():
        if data["mood_scores"]:
            avg_mood = sum(data["mood_scores"]) / len(data["mood_scores"])
            
            for activity_type, minutes in data["activity_types"].items():
                if activity_type not in activity_mood_correlation:
                    activity_mood_correlation[activity_type] = []
                
                activity_mood_correlation[activity_type].append({
                    "mood": avg_mood,
                    "minutes": minutes
                })
    
    # Find activity types that correlate with good moods
    good_mood_activities = []
    for activity_type, correlations_data in activity_mood_correlation.items():
        if len(correlations_data) >= 3:
            avg_mood_for_activity = sum(d["mood"] for d in correlations_data) / len(correlations_data)
            if avg_mood_for_activity >= 7:  # Good mood threshold
                good_mood_activities.append({
                    "activity": activity_type,
                    "avg_mood": round(avg_mood_for_activity, 2)
                })
    
    if good_mood_activities:
        best_activity = max(good_mood_activities, key=lambda x: x["avg_mood"])
        insights.append(f"You tend to be happiest when doing {best_activity['activity']} activities! 😊")
    
    correlations["activity_preferences"] = good_mood_activities
    
    return {
        "correlations": correlations,
        "insights": insights,
        "data_points": len(mood_scores)
    }


@router.get("/quick-check")
async def mood_quick_check(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a quick mood check prompt based on recent entries."""
    # Get recent mood entries
    recent_stmt = select(MoodModel).where(
        MoodModel.user_id == current_user.id
    ).order_by(MoodModel.created_at.desc()).limit(5)
    
    recent_moods = (await db.execute(recent_stmt)).scalars().all()
    
    # Check when last mood was logged
    last_entry = recent_moods[0] if recent_moods else None
    
    if not last_entry:
        return {
            "prompt": "How are you feeling today? This would be your first mood entry!",
            "suggested_tags": ["first-entry", "getting-started"],
            "last_entry": None
        }
    
    hours_since_last = (datetime.now() - last_entry.created_at).total_seconds() / 3600
    
    if hours_since_last < 4:
        return {
            "prompt": "You recently logged your mood. How are you feeling now?",
            "suggested_tags": ["check-in", "update"],
            "last_entry": {
                "mood_score": last_entry.mood_score,
                "created_at": last_entry.created_at,
                "hours_ago": round(hours_since_last, 1)
            }
        }
    elif hours_since_last < 24:
        return {
            "prompt": "It's been a while since your last mood check. How has your day been?",
            "suggested_tags": ["daily-check", "reflection"],
            "last_entry": {
                "mood_score": last_entry.mood_score,
                "created_at": last_entry.created_at,
                "hours_ago": round(hours_since_last, 1)
            }
        }
    else:
        days_since = int(hours_since_last / 24)
        return {
            "prompt": f"Welcome back! It's been {days_since} day{'s' if days_since > 1 else ''} since your last mood entry. How are you feeling?",
            "suggested_tags": ["return", "catch-up"],
            "last_entry": {
                "mood_score": last_entry.mood_score,
                "created_at": last_entry.created_at,
                "days_ago": days_since
            }
        }
