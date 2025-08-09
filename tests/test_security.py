import pytest
from datetime import timedelta
from jose import JWTError
from app.core.security import (
    verify_password, get_password_hash, create_access_token, verify_token
)
from app.core.config import settings


class TestSecurity:
    """Test security functions."""
    
    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_failure(self):
        """Test failed password verification."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False
    
    def test_get_password_hash(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > len(password)
    
    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        assert token is not None
        assert len(token) > 0
        
        # Verify the token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
    
    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)
        assert token is not None
        
        # Verify the token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
    
    def test_verify_token_success(self):
        """Test successful token verification."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        payload = verify_token("invalid_token")
        assert payload is None
    
    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        # Create a token with very short expiry
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(seconds=1)
        token = create_access_token(data, expires_delta=expires_delta)
        
        # Wait for token to expire (this is a simple test)
        import time
        time.sleep(2)
        
        payload = verify_token(token)
        assert payload is None
    
    def test_verify_token_wrong_secret(self):
        """Test token verification with wrong secret key."""
        # Create a token with wrong secret
        data = {"sub": "test@example.com"}
        wrong_secret = "wrong_secret_key"
        
        from jose import jwt
        token = jwt.encode(data, wrong_secret, algorithm=settings.algorithm)
        
        payload = verify_token(token)
        assert payload is None
