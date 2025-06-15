"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    analytics,
    github,
    github_webhooks,
    timer,
    mood,
    vscode,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(github.router, prefix="/github", tags=["github"])
api_router.include_router(
    github_webhooks.router, prefix="/github", tags=["github-webhooks"]
)
api_router.include_router(timer.router, prefix="/timer", tags=["focus-timer"])
api_router.include_router(mood.router, prefix="/mood", tags=["mood-tracker"])
api_router.include_router(vscode.router, prefix="/vscode", tags=["vscode-extension"])
