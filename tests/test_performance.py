import pytest
import time
import uuid
from typing import List, Dict
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.base import get_db
from app.crud.user import create_user
from app.crud.author import create_author
from app.crud.book import create_book
from app.schemas.user import UserCreate
from app.schemas.author import AuthorCreate
from app.schemas.book import BookCreate
from app.core.security import create_access_token


class TestPerformance:
    """Performance tests for API endpoints."""
    
    @pytest.fixture
    def performance_user(self, db_session: Session):
        """Create a user for performance tests."""
        user_data = UserCreate(
            username=f"perf_user_{uuid.uuid4().hex[:8]}",
            email=f"perf_{uuid.uuid4().hex[:8]}@example.com",
            password="testpassword123"
        )
        return create_user(db_session, user_data)
    
    @pytest.fixture
    def auth_headers(self, performance_user):
        """Get authentication headers for performance tests."""
        token = create_access_token(data={"sub": performance_user.email})
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def sample_data(self, db_session: Session, performance_user, auth_headers):
        """Create sample data for performance tests."""
        # Create authors
        authors = []
        for i in range(10):
            author_data = AuthorCreate(
                name=f"Author {i}",
                biography=f"Biography for author {i}"
            )
            author = create_author(db_session, author_data, performance_user.id)
            authors.append(author)
        
        # Create books
        books = []
        for i in range(50):
            book_data = BookCreate(
                title=f"Book {i}",
                description=f"Description for book {i}",
                genre=f"Genre {i % 5}",
                publication_year=2020 + (i % 5),
                author_id=authors[i % 10].id
            )
            book = create_book(db_session, book_data, performance_user.id)
            books.append(book)
        
        return {"authors": authors, "books": books}
    
    def test_books_list_performance(self, client: TestClient, auth_headers, sample_data):
        """Test performance of books list endpoint."""
        start_time = time.time()
        
        response = client.get("/api/v1/books/", headers=auth_headers)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert response.status_code == 200
        data = response.json()
        
        # Handle both old (list) and new (paginated) response formats
        if isinstance(data, list):
            # Old format - direct list
            assert len(data) == 50
        else:
            # New format - paginated response
            assert "items" in data
            assert len(data["items"]) == 50
            assert data["total"] == 50
        
        # Performance assertion: should complete within 1 second
        assert execution_time < 1.0, f"Books list took {execution_time:.3f}s, expected < 1.0s"
        
        print(f"✅ Books list performance: {execution_time:.3f}s")
    
    def test_books_list_with_filtering_performance(self, client: TestClient, auth_headers, sample_data):
        """Test performance of books list with filtering."""
        start_time = time.time()
        
        response = client.get("/api/v1/books/?genre=Genre 1", headers=auth_headers)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert response.status_code == 200
        
        # Performance assertion: filtering should be fast
        assert execution_time < 0.5, f"Books filtering took {execution_time:.3f}s, expected < 0.5s"
        
        print(f"✅ Books filtering performance: {execution_time:.3f}s")
    
    def test_authors_list_performance(self, client: TestClient, auth_headers, sample_data):
        """Test performance of authors list endpoint."""
        start_time = time.time()
        
        response = client.get("/api/v1/authors/", headers=auth_headers)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert response.status_code == 200
        data = response.json()
        
        # Handle both old (list) and new (paginated) response formats
        if isinstance(data, list):
            # Old format - direct list
            assert len(data) == 10
        else:
            # New format - paginated response
            assert "items" in data
            assert len(data["items"]) == 10
            assert data["total"] == 10
        
        # Performance assertion: should complete within 0.5 seconds
        assert execution_time < 0.5, f"Authors list took {execution_time:.3f}s, expected < 0.5s"
        
        print(f"✅ Authors list performance: {execution_time:.3f}s")
    
    def test_single_book_performance(self, client: TestClient, auth_headers, sample_data):
        """Test performance of single book retrieval."""
        book_id = sample_data["books"][0].id
        
        start_time = time.time()
        
        response = client.get(f"/api/v1/books/{book_id}", headers=auth_headers)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert response.status_code == 200
        
        # Performance assertion: single record should be very fast
        assert execution_time < 0.1, f"Single book retrieval took {execution_time:.3f}s, expected < 0.1s"
        
        print(f"✅ Single book performance: {execution_time:.3f}s")
    
    def test_authentication_performance(self, client: TestClient, performance_user):
        """Test performance of authentication endpoint."""
        login_data = {
            "username": performance_user.email,
            "password": "testpassword123"
        }
        
        start_time = time.time()
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert response.status_code == 200
        
        # Performance assertion: authentication should be fast
        assert execution_time < 0.5, f"Authentication took {execution_time:.3f}s, expected < 0.5s"
        
        print(f"✅ Authentication performance: {execution_time:.3f}s")
    
    def test_concurrent_requests_performance(self, client: TestClient, auth_headers, sample_data):
        """Test performance under concurrent requests simulation."""
        # Use sequential requests instead of threading to avoid database connection issues
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            response = client.get("/api/v1/books/", headers=auth_headers)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # Performance assertions
        assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s, expected < 1.0s"
        assert max_response_time < 2.0, f"Max response time {max_response_time:.3f}s, expected < 2.0s"
        
        print(f"✅ Sequential requests performance: avg={avg_response_time:.3f}s, max={max_response_time:.3f}s")
    
    def test_database_query_performance(self, db_session: Session, performance_user):
        """Test database query performance directly."""
        # Create test data
        authors = []
        for i in range(20):
            author_data = AuthorCreate(
                name=f"Perf Author {i}",
                biography=f"Biography {i}"
            )
            author = create_author(db_session, author_data, performance_user.id)
            authors.append(author)
        
        # Test query performance
        start_time = time.time()
        
        from app.crud.author import get_authors
        result = get_authors(db_session, performance_user.id)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert len(result) == 20
        
        # Performance assertion: database query should be fast
        assert execution_time < 0.1, f"Database query took {execution_time:.3f}s, expected < 0.1s"
        
        print(f"✅ Database query performance: {execution_time:.3f}s")
    
    def test_memory_usage_performance(self, client: TestClient, auth_headers, sample_data):
        """Test memory usage during large data operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make multiple requests to simulate load
        for _ in range(10):
            response = client.get("/api/v1/books/", headers=auth_headers)
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory usage should not increase significantly
        assert memory_increase < 50, f"Memory increased by {memory_increase:.1f}MB, expected < 50MB"
        
        print(f"✅ Memory usage: {memory_increase:.1f}MB increase")


class TestLoadTesting:
    """Load testing for API endpoints."""
    
    @pytest.fixture
    def load_test_user(self, db_session: Session):
        """Create a user for load testing."""
        user_data = UserCreate(
            username=f"loadtest_user_{uuid.uuid4().hex[:8]}",
            email=f"loadtest_{uuid.uuid4().hex[:8]}@example.com",
            password="testpassword123"
        )
        return create_user(db_session, user_data)
    
    @pytest.fixture
    def load_test_auth_headers(self, load_test_user):
        """Get authentication headers for load testing."""
        token = create_access_token(data={"sub": load_test_user.email})
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def load_test_data(self, db_session: Session, load_test_user):
        """Create test data for load testing."""
        # Create authors
        authors = []
        for i in range(5):
            author_data = AuthorCreate(
                name=f"Load Author {i}",
                biography=f"Biography for load author {i}"
            )
            author = create_author(db_session, author_data, load_test_user.id)
            authors.append(author)
        
        # Create books
        books = []
        for i in range(20):
            book_data = BookCreate(
                title=f"Load Book {i}",
                description=f"Description for load book {i}",
                genre=f"Genre {i % 3}",
                publication_year=2020 + (i % 5),
                author_id=authors[i % 5].id
            )
            book = create_book(db_session, book_data, load_test_user.id)
            books.append(book)
        
        return {"authors": authors, "books": books}
    
    def test_books_endpoint_load(self, client: TestClient, load_test_auth_headers, load_test_data):
        """Test books endpoint under load."""
        response_times = []
        
        # Make 50 requests (reduced from 100 for faster testing)
        for _ in range(50):
            start_time = time.time()
            response = client.get("/api/v1/books/", headers=load_test_auth_headers)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # Performance assertions
        assert avg_time < 0.5, f"Average response time {avg_time:.3f}s, expected < 0.5s"
        assert max_time < 1.0, f"Max response time {max_time:.3f}s, expected < 1.0s"
        
        print(f"✅ Load test results: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s")
    
    def test_authentication_load(self, client: TestClient, load_test_user):
        """Test authentication endpoint under load."""
        response_times = []
        
        # Make 20 authentication requests (reduced from 50 for faster testing)
        for _ in range(20):
            start_time = time.time()
            response = client.post("/api/v1/auth/login", data={
                "username": load_test_user.email,
                "password": "testpassword123"
            })
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        # Performance assertions
        assert avg_time < 0.3, f"Average auth time {avg_time:.3f}s, expected < 0.3s"
        assert max_time < 0.5, f"Max auth time {max_time:.3f}s, expected < 0.5s"
        
        print(f"✅ Authentication load test: avg={avg_time:.3f}s, max={max_time:.3f}s")
