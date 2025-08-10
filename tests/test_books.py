import os
import pytest
import uuid
from fastapi.testclient import TestClient
from tests.conftest import generate_book_data, generate_author_data


class TestBooks:
    """Test book endpoints."""
    
    def test_create_book_success(self, client: TestClient, auth_headers: dict, created_author: dict):
        """Test successful book creation."""
        book_data = generate_book_data(created_author["id"])
        
        response = client.post("/api/v1/books/", json=book_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == book_data["title"]
        assert data["genre"] == book_data["genre"]
        assert data["publication_year"] == book_data["publication_year"]
        assert data["author_id"] == created_author["id"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_book_unauthorized(self, client: TestClient, created_author: dict):
        """Test book creation without authentication."""
        book_data = generate_book_data(created_author["id"])
        
        response = client.post("/api/v1/books/", json=book_data)
        
        # FastAPI returns 403 Forbidden for missing authentication
        assert response.status_code in [401, 403]

    def test_create_book_invalid_author(self, client: TestClient, auth_headers: dict):
        """Test book creation with invalid author ID."""
        book_data = generate_book_data(999)  # Non-existent author
        
        response = client.post("/api/v1/books/", json=book_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Author not found" in response.json()["detail"]

    def test_create_book_missing_fields(self, client: TestClient, auth_headers: dict, created_author: dict):
        """Test book creation with missing required fields."""
        # Missing title
        book_data = {
            "genre": "Fantasy",
            "publication_year": 1997,
            "author_id": created_author["id"]
        }
        response = client.post("/api/v1/books/", json=book_data, headers=auth_headers)
        assert response.status_code == 422
        
        # Missing author_id
        book_data = {
            "title": "Test Book",
            "genre": "Fantasy",
            "publication_year": 1997
        }
        response = client.post("/api/v1/books/", json=book_data, headers=auth_headers)
        assert response.status_code == 422

    def test_get_books_success(self, client: TestClient, auth_headers: dict, created_author: dict):
        """Test successful retrieval of books."""
        # Create multiple books
        book1 = generate_book_data(created_author["id"])
        book2 = generate_book_data(created_author["id"])
        
        client.post("/api/v1/books/", json=book1, headers=auth_headers)
        client.post("/api/v1/books/", json=book2, headers=auth_headers)
        
        # Get all books
        response = client.get("/api/v1/books/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Handle both list and paginated response formats
        if isinstance(data, list):
            # Simple list format (current implementation)
            assert len(data) >= 2
            book_titles = [book["title"] for book in data]
            assert book1["title"] in book_titles
            assert book2["title"] in book_titles
        else:
            # Paginated format (future implementation)
            assert "items" in data
            assert isinstance(data["items"], list)
            assert len(data["items"]) >= 2
            book_titles = [book["title"] for book in data["items"]]
            assert book1["title"] in book_titles
            assert book2["title"] in book_titles

    def test_get_books_unauthorized(self, client: TestClient):
        """Test getting books without authentication."""
        response = client.get("/api/v1/books/")
        
        # FastAPI returns 403 Forbidden for missing authentication
        assert response.status_code in [401, 403]

    def test_get_book_by_id_success(self, client: TestClient, auth_headers: dict, created_book: dict):
        """Test successful retrieval of book by ID."""
        response = client.get(f"/api/v1/books/{created_book['id']}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_book["id"]
        assert data["title"] == created_book["title"]
        assert data["genre"] == created_book["genre"]

    def test_get_book_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """Test retrieval of non-existent book."""
        response = client.get("/api/v1/books/999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_get_book_by_id_unauthorized(self, client: TestClient):
        """Test getting book by ID without authentication."""
        response = client.get("/api/v1/books/1")
        
        # FastAPI returns 403 Forbidden for missing authentication
        assert response.status_code in [401, 403]

    def test_update_book_success(self, client: TestClient, auth_headers: dict, created_book: dict):
        """Test successful book update."""
        update_data = {
            "title": "Updated Book Title",
            "genre": "Updated Genre",
            "publication_year": 2024
        }
        
        response = client.put(f"/api/v1/books/{created_book['id']}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["genre"] == update_data["genre"]
        assert data["publication_year"] == update_data["publication_year"]

    def test_update_book_partial(self, client: TestClient, auth_headers: dict, created_book: dict):
        """Test partial book update."""
        update_data = {"title": "Partially Updated Title"}
        
        response = client.put(f"/api/v1/books/{created_book['id']}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["genre"] == created_book["genre"]  # Should remain unchanged

    def test_update_book_not_found(self, client: TestClient, auth_headers: dict):
        """Test update of non-existent book."""
        update_data = {"title": "Updated Title", "genre": "Updated Genre"}
        response = client.put("/api/v1/books/999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404

    def test_update_book_unauthorized(self, client: TestClient):
        """Test book update without authentication."""
        update_data = {"title": "Updated Title", "genre": "Updated Genre"}
        response = client.put("/api/v1/books/1", json=update_data)
        
        # FastAPI returns 403 Forbidden for missing authentication
        assert response.status_code in [401, 403]

    def test_delete_book_success(self, client: TestClient, auth_headers: dict, created_book: dict):
        """Test successful book deletion."""
        response = client.delete(f"/api/v1/books/{created_book['id']}", headers=auth_headers)
        
        assert response.status_code == 200
        
        # Verify book is deleted
        get_response = client.get(f"/api/v1/books/{created_book['id']}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_book_not_found(self, client: TestClient, auth_headers: dict):
        """Test deletion of non-existent book."""
        response = client.delete("/api/v1/books/999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_delete_book_unauthorized(self, client: TestClient):
        """Test book deletion without authentication."""
        response = client.delete("/api/v1/books/1")
        
        # FastAPI returns 403 Forbidden for missing authentication
        assert response.status_code in [401, 403]

    def test_books_filtering_by_genre(self, client: TestClient, auth_headers: dict, created_author: dict):
        """Test book filtering by genre."""
        # Create books with different genres
        book1 = generate_book_data(created_author["id"])
        book1["genre"] = "Fantasy"
        book2 = generate_book_data(created_author["id"])
        book2["genre"] = "Science Fiction"
        
        client.post("/api/v1/books/", json=book1, headers=auth_headers)
        client.post("/api/v1/books/", json=book2, headers=auth_headers)
        
        # Filter by genre
        response = client.get("/api/v1/books/?genre=Fantasy", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Handle both list and paginated response formats
        if isinstance(data, list):
            books = data
        else:
            books = data["items"]
        
        assert len(books) >= 1
        assert all(book["genre"] == "Fantasy" for book in books)

    def test_books_filtering_by_publication_year(self, client: TestClient, auth_headers: dict, created_author: dict):
        """Test book filtering by publication year."""
        # Create books with different years
        book1 = generate_book_data(created_author["id"])
        book1["publication_year"] = 2020
        book2 = generate_book_data(created_author["id"])
        book2["publication_year"] = 2023
        
        client.post("/api/v1/books/", json=book1, headers=auth_headers)
        client.post("/api/v1/books/", json=book2, headers=auth_headers)
        
        # Filter by year
        response = client.get("/api/v1/books/?publication_year=2020", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Handle both list and paginated response formats
        if isinstance(data, list):
            books = data
        else:
            books = data["items"]
        
        assert len(books) >= 1
        assert all(book["publication_year"] == 2020 for book in books)

    def test_books_filtering_by_author(self, client: TestClient, auth_headers: dict, created_author: dict):
        """Test book filtering by author."""
        # Create another author
        author2_data = generate_author_data()
        author2_response = client.post("/api/v1/authors/", json=author2_data, headers=auth_headers)
        author2_id = author2_response.json()["id"]
        
        # Create books for different authors
        book1 = generate_book_data(created_author["id"])
        book2 = generate_book_data(author2_id)
        
        client.post("/api/v1/books/", json=book1, headers=auth_headers)
        client.post("/api/v1/books/", json=book2, headers=auth_headers)
        
        # Filter by author
        response = client.get(f"/api/v1/books/?author_id={created_author['id']}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Handle both list and paginated response formats
        if isinstance(data, list):
            books = data
        else:
            books = data["items"]
        
        assert len(books) >= 1
        assert all(book["author_id"] == created_author["id"] for book in books)

    def test_books_pagination(self, client: TestClient, auth_headers: dict, created_author: dict):
        """Test book pagination."""
        # Create multiple books
        for i in range(5):
            book_data = generate_book_data(created_author["id"])
            client.post("/api/v1/books/", json=book_data, headers=auth_headers)
        
        # Test pagination
        response = client.get("/api/v1/books/?skip=0&limit=3", headers=auth_headers)
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

    def test_books_user_isolation(self, client: TestClient):
        """Test that books are isolated per user."""
        # Create two different users
        user1_data = {
            "email": f"user1_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"user1_{uuid.uuid4().hex[:8]}",
            "password": "password123"
        }
        user2_data = {
            "email": f"user2_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"user2_{uuid.uuid4().hex[:8]}",
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
        
        # Create authors and books for each user
        author1_data = generate_author_data()
        author2_data = generate_author_data()
        
        author1_response = client.post("/api/v1/authors/", json=author1_data, headers=headers1)
        author2_response = client.post("/api/v1/authors/", json=author2_data, headers=headers2)
        
        author1_id = author1_response.json()["id"]
        author2_id = author2_response.json()["id"]
        
        book1_data = generate_book_data(author1_id)
        book2_data = generate_book_data(author2_id)
        
        client.post("/api/v1/books/", json=book1_data, headers=headers1)
        client.post("/api/v1/books/", json=book2_data, headers=headers2)
        
        # Check that each user only sees their own books
        response1 = client.get("/api/v1/books/", headers=headers1)
        response2 = client.get("/api/v1/books/", headers=headers2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Handle both list and paginated response formats
        if isinstance(data1, list):
            books1 = data1
            books2 = data2
        else:
            books1 = data1["items"]
            books2 = data2["items"]
        
        # Each user should only see their own book
        assert len(books1) == 1
        assert len(books2) == 1
        assert books1[0]["title"] == book1_data["title"]
        assert books2[0]["title"] == book2_data["title"]

    def test_cascade_delete_author_with_books(self, client: TestClient, auth_headers: dict, created_author: dict):
        """Test that deleting an author also deletes their books."""
        # Create a book for the author
        book_data = generate_book_data(created_author["id"])
        book_response = client.post("/api/v1/books/", json=book_data, headers=auth_headers)
        book_id = book_response.json()["id"]
        
        # Verify book exists
        get_book_response = client.get(f"/api/v1/books/{book_id}", headers=auth_headers)
        assert get_book_response.status_code == 200
        
        # Delete the author
        delete_author_response = client.delete(f"/api/v1/authors/{created_author['id']}", headers=auth_headers)
        assert delete_author_response.status_code == 200
        
        # Verify author is deleted
        get_author_response = client.get(f"/api/v1/authors/{created_author['id']}", headers=auth_headers)
        assert get_author_response.status_code == 404
        
        # Verify book is also deleted
        get_book_response = client.get(f"/api/v1/books/{book_id}", headers=auth_headers)
        assert get_book_response.status_code == 404

    def test_update_book_invalid_author(self, client: TestClient, auth_headers: dict, created_author: dict):
        """Test book update with invalid author ID."""
        # Create a book
        book_data = generate_book_data(created_author["id"])
        book_response = client.post("/api/v1/books/", json=book_data, headers=auth_headers)
        book_id = book_response.json()["id"]
        
        # Try to update with invalid author
        update_data = {"author_id": 999}  # Non-existent author
        response = client.put(f"/api/v1/books/{book_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Author not found" in response.json()["detail"]
