"""Configuration settings for the DevScope backend API."""

import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DevScope API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Backend API for DevScope developer analytics platform"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Security
    SECRET_KEY: str = "your-super-secret-key-for-development-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Supabase Configuration
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY: str = "test-anon-key"
    SUPABASE_SERVICE_KEY: str = "test-service-key"
    JWT_SECRET: str = "test-jwt-secret"

    # Database
    DATABASE_URL: Optional[str] = "sqlite+aiosqlite:///./devscope.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        # Fallback to building PostgreSQL URL if components are provided
        values = info.data if hasattr(info, "data") else {}
        postgres_user = values.get("POSTGRES_USER")
        postgres_password = values.get("POSTGRES_PASSWORD")
        postgres_server = values.get("POSTGRES_SERVER")
        postgres_db = values.get("POSTGRES_DB")

        if all([postgres_user, postgres_password, postgres_server, postgres_db]):
            return PostgresDsn.build(
                scheme="postgresql",
                user=postgres_user,
                password=postgres_password,
                host=postgres_server,
                path=f"/{postgres_db}",
            )

        # Default to SQLite for development
        return "sqlite+aiosqlite:///./devscope.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # External APIs
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # Email Configuration (for future use)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
