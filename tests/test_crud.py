import pytest
from sqlalchemy.orm import Session
from app.crud.user import (
    get_user, get_user_by_email, get_user_by_username, get_users,
    create_user, update_user, delete_user, authenticate_user
)
from app.crud.author import (
    get_author, get_author_by_name, get_authors, create_author,
    update_author, delete_author
)
from app.crud.book import (
    get_book, get_book_by_title, get_books, create_book,
    update_book, delete_book
)
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.author import AuthorCreate, AuthorUpdate
from app.schemas.book import BookCreate, BookUpdate
from app.core.security import get_password_hash


class TestUserCRUD:
    """Test user CRUD operations."""
    
    def test_get_user(self, db_session: Session):
        """Test getting user by ID."""
        # Create a test user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        created_user = create_user(db_session, user_data)
        
        # Test get_user
        user = get_user(db_session, created_user.id)
        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
    
    def test_get_user_not_found(self, db_session: Session):
        """Test getting non-existent user."""
        user = get_user(db_session, 999)
        assert user is None
    
    def test_get_users_pagination(self, db_session: Session):
        """Test getting users with pagination."""
        # Create multiple users
        for i in range(5):
            user_data = UserCreate(
                email=f"test{i}@example.com",
                username=f"testuser{i}",
                password="testpassword123"
            )
            create_user(db_session, user_data)
        
        # Test pagination
        users = get_users(db_session, skip=0, limit=3)
        assert len(users) == 3
        
        users = get_users(db_session, skip=3, limit=3)
        assert len(users) == 2
    
    def test_update_user(self, db_session: Session):
        """Test updating user."""
        # Create a test user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        created_user = create_user(db_session, user_data)
        
        # Update user
        update_data = UserUpdate(email="updated@example.com")
        updated_user = update_user(db_session, created_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.email == "updated@example.com"
        assert updated_user.username == "testuser"  # Should remain unchanged
    
    def test_update_user_not_found(self, db_session: Session):
        """Test updating non-existent user."""
        update_data = UserUpdate(email="updated@example.com")
        result = update_user(db_session, 999, update_data)
        assert result is None
    
    def test_update_user_password(self, db_session: Session):
        """Test updating user password."""
        # Create a test user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        created_user = create_user(db_session, user_data)
        
        # Update password
        update_data = UserUpdate(password="newpassword123")
        updated_user = update_user(db_session, created_user.id, update_data)
        
        assert updated_user is not None
        # Password should be hashed
        assert updated_user.hashed_password != "newpassword123"
    
    def test_delete_user(self, db_session: Session):
        """Test deleting user."""
        # Create a test user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        created_user = create_user(db_session, user_data)
        
        # Delete user
        result = delete_user(db_session, created_user.id)
        assert result is True
        
        # Verify user is deleted
        user = get_user(db_session, created_user.id)
        assert user is None
    
    def test_delete_user_not_found(self, db_session: Session):
        """Test deleting non-existent user."""
        result = delete_user(db_session, 999)
        assert result is False
    
    def test_authenticate_user_success(self, db_session: Session):
        """Test successful user authentication."""
        # Create a test user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        create_user(db_session, user_data)
        
        # Authenticate user
        user = authenticate_user(db_session, "test@example.com", "testpassword123")
        assert user is not None
        assert user.email == "test@example.com"
    
    def test_authenticate_user_wrong_password(self, db_session: Session):
        """Test authentication with wrong password."""
        # Create a test user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        create_user(db_session, user_data)
        
        # Try to authenticate with wrong password
        user = authenticate_user(db_session, "test@example.com", "wrongpassword")
        assert user is None
    
    def test_authenticate_user_not_found(self, db_session: Session):
        """Test authentication with non-existent user."""
        user = authenticate_user(db_session, "nonexistent@example.com", "password")
        assert user is None


class TestAuthorCRUD:
    """Test author CRUD operations."""
    
    def test_get_author_by_name(self, db_session: Session):
        """Test getting author by name."""
        # Create a test user first
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        user = create_user(db_session, user_data)
        
        # Create a test author
        author_data = AuthorCreate(
            name="Test Author",
            biography="Test biography"
        )
        created_author = create_author(db_session, author_data, user.id)
        
        # Test get_author_by_name
        author = get_author_by_name(db_session, "Test Author", user.id)
        assert author is not None
        assert author.name == "Test Author"
    
    def test_get_author_by_name_not_found(self, db_session: Session):
        """Test getting non-existent author by name."""
        # Create a test user first
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        user = create_user(db_session, user_data)
        
        author = get_author_by_name(db_session, "Non-existent Author", user.id)
        assert author is None


class TestBookCRUD:
    """Test book CRUD operations."""
    
    def test_get_book_by_title(self, db_session: Session):
        """Test getting book by title."""
        # Create a test user first
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        user = create_user(db_session, user_data)
        
        # Create a test author
        author_data = AuthorCreate(
            name="Test Author",
            biography="Test biography"
        )
        author = create_author(db_session, author_data, user.id)
        
        # Create a test book
        book_data = BookCreate(
            title="Test Book",
            description="Test description",
            genre="Test",
            publication_year=2023,
            author_id=author.id
        )
        created_book = create_book(db_session, book_data, user.id)
        
        # Test get_book_by_title
        book = get_book_by_title(db_session, "Test Book", user.id)
        assert book is not None
        assert book.title == "Test Book"
    
    def test_get_book_by_title_not_found(self, db_session: Session):
        """Test getting non-existent book by title."""
        # Create a test user first
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        user = create_user(db_session, user_data)
        
        book = get_book_by_title(db_session, "Non-existent Book", user.id)
        assert book is None
