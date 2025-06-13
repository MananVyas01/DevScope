"""Database models for DevScope."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    github_username = Column(String, unique=True, index=True, nullable=True)
    github_id = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    moods = relationship("Mood", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    project_stats = relationship("ProjectStats", back_populates="user", cascade="all, delete-orphan")


class Activity(Base):
    """User activity tracking model."""
    
    __tablename__ = "activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    activity_type = Column(String, nullable=False)  # coding, meeting, break, etc.
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    project = relationship("Project", back_populates="activities")


class Mood(Base):
    """Mood tracking model."""
    
    __tablename__ = "moods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    mood_score = Column(Integer, nullable=False)  # 1-10 scale
    energy_level = Column(Integer, nullable=False)  # 1-5 scale
    stress_level = Column(Integer, nullable=False)  # 1-5 scale
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Array of mood tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="moods")


class Project(Base):
    """Project model for tracking work on different projects."""
    
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    github_repo = Column(String, nullable=True)
    color = Column(String, nullable=True)  # Hex color for UI
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="projects")
    activities = relationship("Activity", back_populates="project", cascade="all, delete-orphan")
    project_stats = relationship("ProjectStats", back_populates="project", cascade="all, delete-orphan")


class ProjectStats(Base):
    """Project statistics aggregation model."""
    
    __tablename__ = "project_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_minutes = Column(Integer, default=0)
    coding_minutes = Column(Integer, default=0)
    meeting_minutes = Column(Integer, default=0)
    break_minutes = Column(Integer, default=0)
    commits_count = Column(Integer, default=0)
    lines_added = Column(Integer, default=0)
    lines_removed = Column(Integer, default=0)
    avg_mood_score = Column(Float, nullable=True)
    avg_energy_level = Column(Float, nullable=True)
    avg_stress_level = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="project_stats")
    project = relationship("Project", back_populates="project_stats")