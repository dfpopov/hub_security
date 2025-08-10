import pytest
import os
import uuid
import multiprocessing
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

# Get process ID for unique database names in parallel execution
PROCESS_ID = multiprocessing.current_process().pid if hasattr(multiprocessing, 'current_process') else os.getpid()

if ISOLATED_MODE:
    # Use SQLite in-memory for isolated testing to support parallel execution
    # Add process ID to ensure unique database per process
    test_db_url = f"sqlite:///./test_isolated_{PROCESS_ID}.db"
    test_engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # Use MySQL for integration testing
    test_engine = create_engine(
        "mysql+pymysql://user:password@localhost:3306/book_collection_test",
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
    # Create tables with check for existing tables
    try:
        Base.metadata.create_all(bind=test_engine)
    except Exception as e:
        # If tables already exist, that's fine for parallel execution
        if "already exists" not in str(e):
            raise
    yield
    # Clean up - drop all tables
    try:
        Base.metadata.drop_all(bind=test_engine)
    except Exception:
        # Ignore errors during cleanup
        pass
    if ISOLATED_MODE:
        # For in-memory database, just dispose the engine
        test_engine.dispose()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provide database session for each test with proper isolation."""
    session = TestingSessionLocal()
    try:
        # Start a transaction
        transaction = session.begin_nested()
        yield session
        # Rollback the transaction to isolate test data
        if transaction.is_active:
            transaction.rollback()
    except Exception:
        # If there's an error, rollback the main session
        session.rollback()
        raise
    finally:
        session.close()


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
def auth_headers(client: TestClient, db_session: Session) -> Dict[str, str]:
    """Provide authentication headers for authenticated requests."""
    # Create unique test user directly in database
    from app.crud.user import create_user
    from app.schemas.user import UserCreate
    from app.core.security import create_access_token
    
    user_data = UserCreate(
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        username=f"testuser_{uuid.uuid4().hex[:8]}",
        password="testpassword123"
    )
    
    # Create user directly in database
    user = create_user(db_session, user_data)
    
    # Commit to ensure user is persisted
    db_session.commit()
    
    # Create access token
    token = create_access_token(data={"sub": user.email})
    
    return {"Authorization": f"Bearer {token}"}


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
