"""Authentication middleware."""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication and authorization."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request with authentication."""
        # For now, this is a placeholder middleware
        # Authentication is handled by dependencies in individual endpoints
        
        # You could add global auth logic here if needed
        # For example, setting user context, checking rate limits per user, etc.
        
        response = await call_next(request)
        return response
