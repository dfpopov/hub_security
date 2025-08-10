import pytest
import os
import uuid
from sqlalchemy.orm import Session
from app.db.session import get_db_session
from app.db.base import get_db
from app.models.user import User
from app.models.author import Author
from app.models.book import Book

# Import test configuration
from tests.conftest import TestingSessionLocal, test_engine


class TestDatabase:
    """Test database functionality."""
    
    def test_get_db_session(self):
        """Test getting a database session."""
        session = get_db_session()
        assert isinstance(session, Session)
        session.close()
    
    def test_session_local(self):
        """Test SessionLocal creation."""
        session = TestingSessionLocal()
        assert isinstance(session, Session)
        session.close()
    
    def test_engine_connection(self):
        """Test database engine connection."""
        # Test that we can connect to the database
        from sqlalchemy import text
        with test_engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.scalar() == 1
    
    def test_model_creation(self):
        """Test that models can be created."""
        session = TestingSessionLocal()
        try:
            # Test User model
            user = User(
                email=f"test_{uuid.uuid4().hex[:8]}@example.com",
                username=f"testuser_{uuid.uuid4().hex[:8]}",
                hashed_password="hashed_password"
            )
            session.add(user)
            session.flush()  # Don't commit, just flush to test
            assert user.id is not None
            
            # Test Author model
            author = Author(
                name="Test Author",
                biography="Test biography",
                user_id=user.id
            )
            session.add(author)
            session.flush()
            assert author.id is not None
            
            # Test Book model
            book = Book(
                title="Test Book",
                description="Test description",
                genre="Test",
                publication_year=2023,
                author_id=author.id,
                user_id=user.id
            )
            session.add(book)
            session.flush()
            assert book.id is not None
            
        finally:
            session.rollback()
            session.close()
    
    def test_get_db_dependency(self):
        """Test get_db dependency function."""
        db_generator = get_db()
        db = next(db_generator)
        assert db is not None
        assert hasattr(db, 'close')
        
        # Test that the generator can be closed properly
        try:
            next(db_generator)
        except StopIteration:
            pass  # Expected behavior
