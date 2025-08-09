import os
from fastapi.testclient import TestClient
from tests.conftest import generate_user_data


class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_user_success(self, client: TestClient):
        """Test successful user registration."""
        user_data = generate_user_data()
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == user_data["username"]
        assert data["user"]["email"] == user_data["email"]
        assert "id" in data["user"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "password" not in data["user"]
        assert "hashed_password" not in data["user"]
        
        # TODO: Add refresh_token check when refresh tokens are implemented
        # if os.getenv("TESTING_MODE") != "isolated":
        #     assert "refresh_token" in data

    def test_register_user_duplicate_email(self, client: TestClient):
        """Test registration with duplicate email."""
        user_data = generate_user_data()
        
        # Register first user
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Try to register with same email
        duplicate_user = user_data.copy()
        duplicate_user["username"] = "differentuser"
        response = client.post("/api/v1/auth/register", json=duplicate_user)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_user_duplicate_username(self, client: TestClient):
        """Test registration with duplicate username."""
        user_data = generate_user_data()
        
        # Register first user
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Try to register with same username
        duplicate_user = user_data.copy()
        duplicate_user["email"] = "different@example.com"
        response = client.post("/api/v1/auth/register", json=duplicate_user)
        
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        user_data = generate_user_data()
        user_data["email"] = "invalid-email"
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422

    def test_register_user_short_password(self, client: TestClient):
        """Test registration with short password."""
        user_data = generate_user_data()
        user_data["password"] = "123"
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422

    def test_login_success_with_email(self, client: TestClient):
        """Test successful login with email."""
        user_data = generate_user_data()
        
        # Register user
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Login with email
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_success_with_username(self, client: TestClient):
        """Test successful login with username."""
        user_data = generate_user_data()
        
        # Register user
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Login with username
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_invalid_password(self, client: TestClient):
        """Test login with invalid password."""
        user_data = generate_user_data()
        
        # Register user
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Login with wrong password
        login_data = {
            "username": user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "somepassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_empty_credentials(self, client: TestClient):
        """Test login with empty credentials."""
        login_data = {
            "username": "",
            "password": ""
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        # FastAPI returns 401 for empty credentials in this case
        assert response.status_code in [401, 422]

    def test_register_user_missing_fields(self, client: TestClient):
        """Test registration with missing required fields."""
        # Test missing email
        user_data = {"username": "testuser", "password": "testpass123"}
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
        
        # Test missing username
        user_data = {"email": "test@example.com", "password": "testpass123"}
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
        
        # Test missing password
        user_data = {"email": "test@example.com", "username": "testuser"}
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_get_current_user(self, client: TestClient, auth_headers: dict):
        """Test getting current user with valid token."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert "password" not in data
        assert "hashed_password" not in data

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")
        # FastAPI returns 403 Forbidden for missing authentication
        assert response.status_code in [401, 403]
