"""Pydantic schemas for request/response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(from_attributes=True)


# User schemas
class UserBase(BaseSchema):
    """Base user schema."""

    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    github_username: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    github_id: Optional[str] = None


class UserLogin(BaseSchema):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    github_username: Optional[str] = None


class UserInDB(UserBase):
    """User schema with database fields."""

    id: UUID
    github_id: Optional[str] = None
    is_active: bool
    is_premium: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None


class User(UserInDB):
    """Public user schema."""

    pass


# Activity schemas
class ActivityBase(BaseSchema):
    """Base activity schema."""

    activity_type: str = Field(
        ..., description="Type of activity (coding, meeting, break, etc.)"
    )
    description: Optional[str] = None
    duration_minutes: int = Field(..., ge=0, description="Duration in minutes")
    project_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    started_at: datetime
    ended_at: Optional[datetime] = None


class ActivityCreate(ActivityBase):
    """Schema for creating an activity."""

    pass


class ActivityUpdate(BaseSchema):
    """Schema for updating an activity."""

    activity_type: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    project_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    ended_at: Optional[datetime] = None


class ActivityInDB(ActivityBase):
    """Activity schema with database fields."""

    id: UUID
    user_id: UUID
    created_at: datetime


class Activity(ActivityInDB):
    """Public activity schema."""

    pass


# Mood schemas
class MoodBase(BaseSchema):
    """Base mood schema."""

    mood_score: int = Field(..., ge=1, le=10, description="Mood score (1-10)")
    energy_level: int = Field(..., ge=1, le=5, description="Energy level (1-5)")
    stress_level: int = Field(..., ge=1, le=5, description="Stress level (1-5)")
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class MoodCreate(MoodBase):
    """Schema for creating a mood entry."""

    pass


class MoodUpdate(BaseSchema):
    """Schema for updating a mood entry."""

    mood_score: Optional[int] = Field(None, ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    stress_level: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class MoodInDB(MoodBase):
    """Mood schema with database fields."""

    id: UUID
    user_id: UUID
    created_at: datetime


class Mood(MoodInDB):
    """Public mood schema."""

    pass


# Project schemas
class ProjectBase(BaseSchema):
    """Base project schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    github_repo: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(BaseSchema):
    """Schema for updating a project."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    github_repo: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active: Optional[bool] = None


class ProjectInDB(ProjectBase):
    """Project schema with database fields."""

    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class Project(ProjectInDB):
    """Public project schema."""

    pass


# Project stats schemas
class ProjectStatsBase(BaseSchema):
    """Base project stats schema."""

    date: datetime
    total_minutes: int = 0
    coding_minutes: int = 0
    meeting_minutes: int = 0
    break_minutes: int = 0
    commits_count: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    avg_mood_score: Optional[float] = None
    avg_energy_level: Optional[float] = None
    avg_stress_level: Optional[float] = None


class ProjectStatsCreate(ProjectStatsBase):
    """Schema for creating project stats."""

    project_id: UUID


class ProjectStatsUpdate(BaseSchema):
    """Schema for updating project stats."""

    total_minutes: Optional[int] = None
    coding_minutes: Optional[int] = None
    meeting_minutes: Optional[int] = None
    break_minutes: Optional[int] = None
    commits_count: Optional[int] = None
    lines_added: Optional[int] = None
    lines_removed: Optional[int] = None
    avg_mood_score: Optional[float] = None
    avg_energy_level: Optional[float] = None
    avg_stress_level: Optional[float] = None


class ProjectStatsInDB(ProjectStatsBase):
    """Project stats schema with database fields."""

    id: UUID
    user_id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProjectStats(ProjectStatsInDB):
    """Public project stats schema."""

    pass


# Analytics schemas
class DailyStats(BaseSchema):
    """Daily statistics summary."""

    date: datetime
    total_minutes: int
    activity_breakdown: Dict[str, int]
    avg_mood_score: Optional[float] = None
    avg_energy_level: Optional[float] = None
    avg_stress_level: Optional[float] = None
    projects_worked: int


class WeeklyStats(BaseSchema):
    """Weekly statistics summary."""

    week_start: datetime
    week_end: datetime
    total_minutes: int
    daily_breakdown: List[DailyStats]
    top_activities: List[Dict[str, Any]]
    mood_trend: List[Dict[str, Any]]
    productivity_score: Optional[float] = None


class MonthlyStats(BaseSchema):
    """Monthly statistics summary."""

    month: int
    year: int
    total_minutes: int
    weekly_breakdown: List[WeeklyStats]
    top_projects: List[Dict[str, Any]]
    avg_daily_minutes: float
    most_productive_day: Optional[str] = None


# Timer schemas
class TimerSession(BaseSchema):
    """Timer session schema."""

    project_id: Optional[UUID] = None
    activity_type: str = "coding"
    description: Optional[str] = None
    duration_minutes: int = Field(..., ge=1, le=240)  # Max 4 hours
    tags: Optional[List[str]] = None


class TimerSessionResponse(BaseSchema):
    """Timer session response."""

    session_id: UUID
    project_id: Optional[UUID] = None
    activity_type: str
    description: Optional[str] = None
    duration_minutes: int
    started_at: datetime
    estimated_end: datetime
    tags: Optional[List[str]] = None


# GitHub schemas
class GitHubRepo(BaseSchema):
    """GitHub repository schema."""

    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    clone_url: str
    language: Optional[str] = None
    stargazers_count: int
    forks_count: int
    updated_at: datetime


class GitHubCommit(BaseSchema):
    """GitHub commit schema."""

    sha: str
    message: str
    author: str
    date: datetime
    additions: int
    deletions: int
    files_changed: int


class GitHubStats(BaseSchema):
    """GitHub statistics schema."""

    total_commits: int
    total_repos: int
    languages: Dict[str, int]
    recent_commits: List[GitHubCommit]
    contribution_streak: int


# Authentication schemas
class Token(BaseSchema):
    """Token schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseSchema):
    """Token refresh schema."""

    refresh_token: str


class AuthCallback(BaseSchema):
    """OAuth callback schema."""

    code: str
    state: Optional[str] = None


# Response schemas
class MessageResponse(BaseSchema):
    """Generic message response."""

    message: str


class ErrorResponse(BaseSchema):
    """Error response schema."""

    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
