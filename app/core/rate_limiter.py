from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Disable rate limiting in test environment
if settings.debug:
    limiter.enabled = False
