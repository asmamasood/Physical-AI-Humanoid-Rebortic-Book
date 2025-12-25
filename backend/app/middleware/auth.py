"""
Authentication middleware for RAG Chatboard.

Provides admin authentication and user session verification.
"""

from typing import Optional
from fastapi import Request, HTTPException, Security, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..config import get_settings


# HTTP Bearer security scheme
security = HTTPBearer()


async def verify_admin(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> bool:
    """
    Verify admin authentication for protected endpoints.
    
    Checks the Authorization header for Bearer token matching ADMIN_SECRET.
    """
    settings = get_settings()
    expected_token = settings.admin_secret
    
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return True


async def verify_admin_optional(request: Request) -> bool:
    """
    Optional admin verification - returns False instead of raising exception.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return False
    
    if not auth_header.startswith("Bearer "):
        return False
    
    token = auth_header.replace("Bearer ", "")
    settings = get_settings()
    
    return token == settings.admin_secret


async def get_user_id_optional(x_user_id: Optional[str] = Header(None)) -> Optional[str]:
    """
    Extract user ID from X-User-ID header (set by frontend after auth).
    Returns None if not authenticated.
    """
    return x_user_id


async def require_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """
    Require user ID for protected routes.
    Raises 401 if not authenticated.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in."
        )
    return x_user_id
