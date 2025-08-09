from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.rate_limiter import limiter
from app.api import auth, author, book

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    debug=settings.debug,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.api_v1_str}/auth", tags=["authentication"])
app.include_router(author.router, prefix=f"{settings.api_v1_str}/authors", tags=["authors"])
app.include_router(book.router, prefix=f"{settings.api_v1_str}/books", tags=["books"])


@app.get("/")
@limiter.limit("10/minute")
def read_root(request: Request):
    """Root endpoint with rate limiting."""
    return {"message": "Welcome to Book Collection API"}


@app.get("/health")
@limiter.limit("30/minute")
def health_check(request: Request):
    """Health check endpoint with rate limiting."""
    return {"status": "healthy"}
