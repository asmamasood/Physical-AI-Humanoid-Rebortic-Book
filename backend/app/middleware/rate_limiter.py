"""
Rate limiting middleware for RAG Chatboard.

Implements IP-based rate limiting to prevent API abuse.
"""

import time
from collections import defaultdict
from typing import Dict, List

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request

from ..config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple IP-based rate limiting middleware.
    
    Tracks requests per IP address per minute and returns 429
    when the limit is exceeded.
    """
    
    def __init__(self, app, requests_per_minute: int = None):
        """
        Initialize rate limiter.
        
        Args:
            app: ASGI application
            requests_per_minute: Max requests per IP per minute
        """
        super().__init__(app)
        
        if requests_per_minute is None:
            settings = get_settings()
            requests_per_minute = settings.rate_limit_per_minute
        
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request through rate limiter.
        """
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/meta"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        now = time.time()
        
        # Clean old requests (older than 60 seconds)
        self.requests[client_ip] = [
            timestamp for timestamp in self.requests[client_ip]
            if now - timestamp < 60
        ]
        
        # Check if rate limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.requests_per_minute} requests per minute"
                },
                headers={"Retry-After": "60"}
            )
        
        # Record this request
        self.requests[client_ip].append(now)
        
        # Process request
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.
        
        Handles X-Forwarded-For header for requests behind proxies.
        """
        # Check for X-Forwarded-For header (common with reverse proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
