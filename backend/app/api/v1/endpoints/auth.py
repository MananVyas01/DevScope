"""Authentication endpoints."""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.dependencies import get_current_user, verify_supabase_token
from app.auth.supabase_auth import SupabaseAuth
from app.config import settings
from app.schemas.schemas import Token, User, UserCreate, UserLogin

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer()
supabase_auth = SupabaseAuth()


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(user_data: UserLogin, request: Request) -> Any:
    """
    Login with email and password.
    For development - in production, use Supabase client-side auth.
    """
    try:
        # This would typically be handled client-side with Supabase
        # Here we just validate the token if provided
        if hasattr(user_data, "access_token"):
            user = await verify_supabase_token(user_data.access_token)
            return {
                "access_token": user_data.access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use Supabase client-side authentication",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e


@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request, current_user: User = Depends(get_current_user)
) -> Any:
    """Refresh access token."""
    try:
        # In a real implementation, you'd generate a new token
        # For now, return the same token with extended expiry
        return {
            "access_token": "refreshed_token",  # This should be a new JWT
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not refresh token"
        ) from e


@router.post("/verify")
@limiter.limit("20/minute")
async def verify_token(
    request: Request, current_user: User = Depends(get_current_user)
) -> Any:
    """Verify if the current token is valid."""
    return {"valid": True, "user": current_user, "verified_at": datetime.utcnow()}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)) -> Any:
    """
    Logout user.
    In Supabase, this is typically handled client-side.
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> Any:
    """Get current user information."""
    return current_user


@router.post("/github/callback")
@limiter.limit("10/minute")
async def github_callback(request: Request, code: str) -> Any:
    """
    Handle GitHub OAuth callback.
    This would typically be handled by Supabase automatically.
    """
    try:
        # In a real implementation, you'd exchange the code for tokens
        # and create/update the user in your database
        return {
            "message": "GitHub authentication successful",
            "redirect_url": f"{settings.FRONTEND_URL}/dashboard",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub authentication failed",
        ) from e
