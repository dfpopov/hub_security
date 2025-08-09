import pytest
import os
import uuid
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.db.base_class import Base
from app.core.config import settings
from app.api.deps import get_db


# Check if we're running in isolated mode
ISOLATED_MODE = os.getenv("TESTING_MODE") == "isolated"

if ISOLATED_MODE:
    # Use SQLite file for isolated testing (to avoid in-memory connection issues)
    test_db_url = "sqlite:///./test_isolated.db"
    test_engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # Use MySQL for integration testing
    test_engine = create_engine(
        "mysql+pymysql://user:password@db:3306/book_collection_test",
        pool_pre_ping=True,
        echo=False
    )

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database for the entire test session."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Clean up - drop all tables and remove file
    Base.metadata.drop_all(bind=test_engine)
    if ISOLATED_MODE:
        import os
        import time
        try:
            # Close all database connections first
            test_engine.dispose()
            # Wait a bit for file handles to be released
            time.sleep(0.1)
            os.remove("./test_isolated.db")
        except (FileNotFoundError, PermissionError):
            # File will be cleaned up on next run or by OS
            pass


@pytest.fixture(autouse=True)
def setup_database_for_test():
    """Ensure database is set up for each test."""
    # Create tables if they don't exist
    print(f"Creating tables with engine: {test_engine}")
    print(f"Base metadata tables: {list(Base.metadata.tables.keys())}")
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide database session for each test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        
        # Clean up all data after each test
        cleanup_session = TestingSessionLocal()
        try:
            for table in reversed(Base.metadata.sorted_tables):
                cleanup_session.execute(table.delete())
            cleanup_session.commit()
        finally:
            cleanup_session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient) -> Dict[str, str]:
    """Provide authentication headers for authenticated requests."""
    # Create unique test user
    user_data = {
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "username": f"testuser_{uuid.uuid4().hex[:8]}",
        "password": "testpassword123"
    }
    
    # Register user
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200, f"Registration failed: {response.json()}"
    
    # Login to get token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200, f"Login failed: {response.json()}"
    
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture
def sample_author_data() -> Dict[str, Any]:
    """Provide sample author data for testing."""
    return {
        "name": f"Test Author {uuid.uuid4().hex[:8]}",
        "biography": "A test author for unit testing"
    }


@pytest.fixture
def sample_book_data() -> Dict[str, Any]:
    """Provide sample book data for testing."""
    return {
        "title": f"Test Book {uuid.uuid4().hex[:8]}",
        "description": "A test book for unit testing",
        "genre": "Test",
        "publication_year": 2023,
        "author_id": None  # Will be set by the fixture
    }


@pytest.fixture
def created_author(client: TestClient, auth_headers: Dict[str, str], sample_author_data: Dict[str, Any]) -> Dict[str, Any]:
    """Provide a created author for testing."""
    response = client.post("/api/v1/authors/", json=sample_author_data, headers=auth_headers)
    assert response.status_code == 200, f"Author creation failed: {response.json()}"
    return response.json()


@pytest.fixture
def created_book(client: TestClient, auth_headers: Dict[str, str], created_author: Dict[str, Any], sample_book_data: Dict[str, Any]) -> Dict[str, Any]:
    """Provide a created book for testing."""
    book_data = sample_book_data.copy()
    book_data["author_id"] = created_author["id"]
    response = client.post("/api/v1/books/", json=book_data, headers=auth_headers)
    assert response.status_code == 200, f"Book creation failed: {response.json()}"
    return response.json()


# Helper functions for generating test data
def generate_author_data() -> Dict[str, Any]:
    """Generate random author data."""
    return {
        "name": f"Author {uuid.uuid4().hex[:8]}",
        "biography": f"Biography for {uuid.uuid4().hex[:8]}"
    }


def generate_book_data(author_id: int) -> Dict[str, Any]:
    """Generate random book data."""
    return {
        "title": f"Book {uuid.uuid4().hex[:8]}",
        "description": f"Description for {uuid.uuid4().hex[:8]}",
        "genre": "Test",
        "publication_year": 2023,
        "author_id": author_id
    }


def generate_user_data() -> Dict[str, Any]:
    """Generate random user data."""
    return {
        "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "password": "testpassword123"
    }
