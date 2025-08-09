from typing import Optional
from sqlalchemy.orm import Session
from app.crud.user import (
    get_user, get_user_by_email, get_user_by_username, 
    create_user, update_user, delete_user, authenticate_user
)
from app.schemas.user import UserCreate, UserUpdate, User
from app.core.security import get_password_hash, verify_password


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with business logic validation."""
        # Business logic: validate email format
        if "@" not in user_data.email or "." not in user_data.email:
            raise ValueError("Invalid email format")
        
        # Business logic: validate password strength
        if len(user_data.password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Business logic: check for common weak passwords
        weak_passwords = ["password", "123456", "qwerty", "admin"]
        if user_data.password.lower() in weak_passwords:
            raise ValueError("Password is too weak")
        
        # Business logic: validate username
        if len(user_data.username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        # Check if user already exists
        if get_user_by_email(self.db, user_data.email):
            raise ValueError("Email already registered")
        
        if get_user_by_username(self.db, user_data.username):
            raise ValueError("Username already taken")
        
        return create_user(self.db, user_data)
    
    def authenticate_user(self, username_or_email: str, password: str) -> Optional[User]:
        """Authenticate user with business logic."""
        # Business logic: validate input
        if not username_or_email or not password:
            return None
        
        # Try to find user by email first, then by username
        user = get_user_by_email(self.db, username_or_email)
        if not user:
            user = get_user_by_username(self.db, username_or_email)
        
        if not user:
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return get_user(self.db, user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return get_user_by_email(self.db, email)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user with business logic validation."""
        user = get_user(self.db, user_id)
        if not user:
            return None
        
        # Business logic: validate email if provided
        if user_data.email and "@" not in user_data.email:
            raise ValueError("Invalid email format")
        
        # Business logic: validate password strength if provided
        if user_data.password:
            if len(user_data.password) < 8:
                raise ValueError("Password must be at least 8 characters long")
            
            weak_passwords = ["password", "123456", "qwerty", "admin"]
            if user_data.password.lower() in weak_passwords:
                raise ValueError("Password is too weak")
        
        return update_user(self.db, user_id, user_data)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user with business logic."""
        user = get_user(self.db, user_id)
        if not user:
            return False
        
        # Business logic: check if user has active data
        # In a real application, you might want to check for active sessions,
        # pending transactions, etc.
        
        return delete_user(self.db, user_id)
