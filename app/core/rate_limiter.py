from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings
from fastapi import Request
from typing import Optional

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Disable rate limiting in test environment
if settings.debug:
    limiter.enabled = False


def get_user_key(request: Request) -> str:
    """Get user-specific key for rate limiting."""
    # Try to get user from JWT token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            from app.core.security import verify_token
            payload = verify_token(token)
            if payload and payload.get("sub"):
                return f"user:{payload['sub']}"
        except:
            pass
    
    # Fallback to IP address
    return f"ip:{get_remote_address(request)}"


def get_user_rate_limit_key(request: Request) -> str:
    """Get rate limit key for authenticated users."""
    return get_user_key(request)
