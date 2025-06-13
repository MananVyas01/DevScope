"""Supabase authentication integration."""

import asyncio
from typing import Optional, Dict, Any
import jwt
from supabase import create_client, Client
import structlog

from app.config import settings

logger = structlog.get_logger()


class SupabaseAuth:
    """Supabase authentication handler."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_KEY
        )
        self.anon_client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token with Supabase.
        """
        try:
            # Decode the JWT token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.ALGORITHM],
                audience="authenticated"
            )
            
            logger.info("Token verified successfully", user_id=payload.get("sub"))
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise ValueError("Token has expired")
        except jwt.JWTError as e:
            logger.error("JWT decode error", error=str(e))
            raise ValueError("Invalid token")
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by ID from Supabase.
        """
        try:
            result = self.client.auth.admin.get_user_by_id(user_id)
            if result.user:
                return {
                    "id": result.user.id,
                    "email": result.user.email,
                    "user_metadata": result.user.user_metadata,
                    "app_metadata": result.user.app_metadata,
                    "created_at": result.user.created_at,
                    "updated_at": result.user.updated_at,
                }
            return None
        except Exception as e:
            logger.error("Error fetching user", user_id=user_id, error=str(e))
            return None
    
    async def create_user(self, email: str, password: str, user_metadata: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new user in Supabase.
        """
        try:
            result = self.client.auth.admin.create_user({
                "email": email,
                "password": password,
                "user_metadata": user_metadata or {},
                "email_confirm": True
            })
            
            if result.user:
                logger.info("User created successfully", user_id=result.user.id, email=email)
                return {
                    "id": result.user.id,
                    "email": result.user.email,
                    "user_metadata": result.user.user_metadata,
                    "created_at": result.user.created_at,
                }
            return None
            
        except Exception as e:
            logger.error("Error creating user", email=email, error=str(e))
            raise ValueError(f"Could not create user: {str(e)}")
    
    async def update_user_metadata(self, user_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update user metadata in Supabase.
        """
        try:
            result = self.client.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": metadata}
            )
            
            if result.user:
                logger.info("User metadata updated", user_id=user_id)
                return True
            return False
            
        except Exception as e:
            logger.error("Error updating user metadata", user_id=user_id, error=str(e))
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from Supabase.
        """
        try:
            self.client.auth.admin.delete_user(user_id)
            logger.info("User deleted", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Error deleting user", user_id=user_id, error=str(e))
            return False
    
    async def refresh_session(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh user session with refresh token.
        """
        try:
            result = self.anon_client.auth.refresh_session(refresh_token)
            if result.session:
                return {
                    "access_token": result.session.access_token,
                    "refresh_token": result.session.refresh_token,
                    "expires_in": result.session.expires_in,
                    "token_type": result.session.token_type,
                    "user": {
                        "id": result.session.user.id,
                        "email": result.session.user.email,
                        "user_metadata": result.session.user.user_metadata,
                    }
                }
            return None
            
        except Exception as e:
            logger.error("Error refreshing session", error=str(e))
            return None
    
    async def sign_out(self, token: str) -> bool:
        """
        Sign out user (invalidate token).
        Note: In Supabase, tokens are stateless, so this is mainly for logging.
        """
        try:
            # In a real implementation, you might want to blacklist the token
            # For now, we'll just log the sign out
            payload = await self.verify_token(token)
            user_id = payload.get("sub")
            logger.info("User signed out", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Error during sign out", error=str(e))
            return False
