from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.crud.user import get_user_by_email
from app.db.base import get_db
from app.core.security import create_access_token, create_refresh_token, verify_refresh_token
from app.core.config import settings
from app.services.user_service import UserService
from app.api.deps import get_current_user
from app.schemas.user import UserCreate, User, Token, UserRegisterResponse
from app.core.rate_limiter import limiter, get_user_rate_limit_key

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get user service."""
    return UserService(db)

@router.post("/register", response_model=UserRegisterResponse)
@limiter.limit("5/minute", key_func=get_user_rate_limit_key)
def register(
    user: UserCreate, 
    request: Request,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user and return user data with access token."""
    try:
        # Create the user using service layer
        created_user = user_service.create_user(user)
        
        # Generate tokens for the new user
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": created_user.email}, expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            data={"sub": created_user.email}
        )
        
        return {
            "user": created_user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
@limiter.limit("10/minute", key_func=get_user_rate_limit_key)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    user_service: UserService = Depends(get_user_service)
):
    """Login user and return access token."""
    # Authenticate user by email or username
    user = user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.email}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=User)
def get_current_user(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    # Verify refresh token
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    email = payload.get("sub")
    user = get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate new tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    new_refresh_token = create_refresh_token(
        data={"sub": user.email}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
