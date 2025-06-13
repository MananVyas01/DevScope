"""Authentication dependencies for FastAPI."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.auth.supabase_auth import SupabaseAuth
from app.config import settings
from app.schemas.schemas import User

security = HTTPBearer()
supabase_auth = SupabaseAuth()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token.
    """
    token = credentials.credentials
    
    try:
        # Verify the Supabase JWT token
        user = await verify_supabase_token(token)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def verify_supabase_token(token: str) -> User:
    """
    Verify Supabase JWT token and return user information.
    """
    try:
        # Decode the JWT token using Supabase JWT secret
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            audience="authenticated"
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID found"
            )
        
        # Extract user information from token
        user_metadata = payload.get("user_metadata", {})
        email = payload.get("email")
        
        return User(
            id=user_id,
            email=email,
            full_name=user_metadata.get("full_name"),
            avatar_url=user_metadata.get("avatar_url"),
            provider=payload.get("app_metadata", {}).get("provider"),
            created_at=payload.get("created_at"),
            updated_at=payload.get("updated_at")
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for endpoints that work for both authenticated and anonymous users.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_roles(*roles: str):
    """
    Dependency factory for role-based access control.
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # In a real implementation, you'd check user roles from database
        # For now, we'll assume all authenticated users have basic access
        user_roles = getattr(current_user, 'roles', ['user'])
        
        if not any(role in user_roles for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


def require_verified_email(current_user: User = Depends(get_current_user)) -> User:
    """
    Require user to have verified email.
    """
    if not getattr(current_user, 'email_verified', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user
