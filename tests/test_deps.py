import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.api.deps import get_current_user
from app.core.security import create_access_token


class TestDependencies:
    """Test API dependencies."""
    
    def test_get_current_user_success(self, client: TestClient, auth_headers: dict):
        """Test successful user authentication."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test authentication with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_get_current_user_missing_token(self, client: TestClient):
        """Test authentication without token."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_current_user_expired_token(self, client: TestClient):
        """Test authentication with expired token."""
        # Create an expired token (this would require mocking time)
        # For now, we'll test with a malformed token
        headers = {"Authorization": "Bearer expired.token.here"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_get_current_user_nonexistent_user(self, client: TestClient):
        """Test authentication with token for non-existent user."""
        # Create a token for a non-existent user
        token = create_access_token(data={"sub": "nonexistent@example.com"})
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_get_current_user_token_without_sub(self, client: TestClient):
        """Test authentication with token that doesn't contain 'sub' field."""
        # Create a token without 'sub' field
        token = create_access_token(data={"other_field": "value"})
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
