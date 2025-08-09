import os
import pytest
from fastapi.testclient import TestClient
from tests.conftest import generate_author_data


class TestAuthors:
    """Test author endpoints."""
    
    def test_create_author_success(self, client: TestClient, auth_headers: dict):
        """Test successful author creation."""
        author_data = generate_author_data()
        
        response = client.post("/api/v1/authors/", json=author_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == author_data["name"]
        assert data["biography"] == author_data["biography"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_author_unauthorized(self, client: TestClient):
        """Test author creation without authentication."""
        author_data = generate_author_data()
        
        response = client.post("/api/v1/authors/", json=author_data)
        
        # FastAPI returns 403 Forbidden for missing authentication
        assert response.status_code in [401, 403]

    def test_create_author_missing_fields(self, client: TestClient, auth_headers: dict):
        """Test author creation with missing required fields."""
        # Missing name
        author_data = {"biography": "Some biography"}
        response = client.post("/api/v1/authors/", json=author_data, headers=auth_headers)
        assert response.status_code == 422
        
        # Missing biography
        author_data = {"name": "Test Author"}
        response = client.post("/api/v1/authors/", json=author_data, headers=auth_headers)
        assert response.status_code == 422

    def test_get_authors_success(self, client: TestClient, auth_headers: dict):
        """Test successful retrieval of authors."""
        # Create multiple authors
        author1 = generate_author_data()
        author2 = generate_author_data()
        
        client.post("/api/v1/authors/", json=author1, headers=auth_headers)
        client.post("/api/v1/authors/", json=author2, headers=auth_headers)
        
        # Get all authors
        response = client.get("/api/v1/authors/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Handle both list and paginated response formats
        if isinstance(data, list):
            # Simple list format (current implementation)
            assert len(data) >= 2
            author_names = [author["name"] for author in data]
            assert author1["name"] in author_names
            assert author2["name"] in author_names
        else:
            # Paginated format (future implementation)
            assert "items" in data
            assert isinstance(data["items"], list)
            assert len(data["items"]) >= 2
            author_names = [author["name"] for author in data["items"]]
            assert author1["name"] in author_names
            assert author2["name"] in author_names

    def test_get_authors_unauthorized(self, client: TestClient):
        """Test getting authors without authentication."""
        response = client.get("/api/v1/authors/")
        
        # FastAPI returns 403 Forbidden for missing authentication
        assert response.status_code in [401, 403]

    def test_get_author_by_id_success(self, client: TestClient, auth_headers: dict):
        """Test successful retrieval of author by ID."""
        author_data = generate_author_data()
        
        # Create author
        create_response = client.post("/api/v1/authors/", json=author_data, headers=auth_headers)
        assert create_response.status_code == 200
        author_id = create_response.json()["id"]
        
        # Get author by ID
        response = client.get(f"/api/v1/authors/{author_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == author_id
        assert data["name"] == author_data["name"]
        assert data["biography"] == author_data["biography"]

    def test_get_author_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """Test retrieval of non-existent author."""
        response = client.get("/api/v1/authors/999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_get_author_by_id_unauthorized(self, client: TestClient):
        """Test getting author by ID without authentication."""
        response = client.get("/api/v1/authors/1")
        
        # FastAPI returns 403 Forbidden for missing authentication
        assert response.status_code in [401, 403]

    def test_update_author_success(self, client: TestClient, auth_headers: dict):
        """Test successful author update."""
        author_data = generate_author_data()
        
        # Create author
        create_response = client.post("/api/v1/authors/", json=author_data, headers=auth_headers)
        assert create_response.status_code == 200
        author_id = create_response.json()["id"]
        
        # Update author
        update_data = {
            "name": "Updated Author Name",
            "biography": "Updated biography"
        }
        response = client.put(f"/api/v1/authors/{author_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == author_id
        assert data["name"] == update_data["name"]
        assert data["biography"] == update_data["biography"]

    def test_update_author_partial(self, client: TestClient, auth_headers: dict):
        """Test partial author update."""
        author_data = generate_author_data()
        
        # Create author
        create_response = client.post("/api/v1/authors/", json=author_data, headers=auth_headers)
        assert create_response.status_code == 200
        author_id = create_response.json()["id"]
        
        # Update only name
        update_data = {"name": "Partially Updated Name"}
        response = client.put(f"/api/v1/authors/{author_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["biography"] == author_data["biography"]  # Should remain unchanged

    def test_update_author_not_found(self, client: TestClient, auth_headers: dict):
        """Test update of non-existent author."""
        update_data = {"name": "Updated Name", "biography": "Updated biography"}
        response = client.put("/api/v1/authors/999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404

    def test_update_author_unauthorized(self, client: TestClient):
        """Test author update without authentication."""
        update_data = {"name": "Updated Name", "biography": "Updated biography"}
        response = client.put("/api/v1/authors/1", json=update_data)
        
        # FastAPI returns 403 Forbidden for missing authentication
        assert response.status_code in [401, 403]

    def test_delete_author_success(self, client: TestClient, auth_headers: dict):
        """Test successful author deletion."""
        author_data = generate_author_data()
        
        # Create author
        create_response = client.post("/api/v1/authors/", json=author_data, headers=auth_headers)
        assert create_response.status_code == 200
        author_id = create_response.json()["id"]
        
        # Delete author
        response = client.delete(f"/api/v1/authors/{author_id}", headers=auth_headers)
        
        assert response.status_code == 200
        
        # Verify author is deleted
        get_response = client.get(f"/api/v1/authors/{author_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_author_not_found(self, client: TestClient, auth_headers: dict):
        """Test deletion of non-existent author."""
        response = client.delete("/api/v1/authors/999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_delete_author_unauthorized(self, client: TestClient):
        """Test author deletion without authentication."""
        response = client.delete("/api/v1/authors/1")
        
        # FastAPI returns 403 Forbidden for missing authentication
        assert response.status_code in [401, 403]

    def test_authors_pagination(self, client: TestClient, auth_headers: dict):
        """Test author pagination."""
        # Create multiple authors
        for i in range(5):
            author_data = generate_author_data()
            client.post("/api/v1/authors/", json=author_data, headers=auth_headers)
        
        # Test pagination
        response = client.get("/api/v1/authors/?skip=0&limit=3", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        
        # Handle both list and paginated response formats
        if isinstance(data, list):
            # Simple list format (current implementation)
            assert len(data) <= 3
        else:
            # Paginated format (future implementation)
            assert "items" in data
            assert len(data["items"]) <= 3
            assert "total" in data
            assert "page" in data
            assert "size" in data

    def test_authors_user_isolation(self, client: TestClient):
        """Test that authors are isolated per user."""
        # Create two different users
        user1_data = {
            "email": "user1@example.com",
            "username": "user1",
            "password": "password123"
        }
        user2_data = {
            "email": "user2@example.com",
            "username": "user2",
            "password": "password123"
        }
        
        # Register users
        response1 = client.post("/api/v1/auth/register", json=user1_data)
        response2 = client.post("/api/v1/auth/register", json=user2_data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Get tokens
        token1 = response1.json()["access_token"]
        token2 = response2.json()["access_token"]
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Create authors for each user
        author1_data = generate_author_data()
        author2_data = generate_author_data()
        
        client.post("/api/v1/authors/", json=author1_data, headers=headers1)
        client.post("/api/v1/authors/", json=author2_data, headers=headers2)
        
        # Check that each user only sees their own authors
        response1 = client.get("/api/v1/authors/", headers=headers1)
        response2 = client.get("/api/v1/authors/", headers=headers2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Handle both list and paginated response formats
        if isinstance(data1, list):
            authors1 = data1
            authors2 = data2
        else:
            authors1 = data1["items"]
            authors2 = data2["items"]
        
        # Each user should only see their own author
        assert len(authors1) == 1
        assert len(authors2) == 1
        assert authors1[0]["name"] == author1_data["name"]
        assert authors2[0]["name"] == author2_data["name"]
