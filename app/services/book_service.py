from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.book import get_books, get_book, create_book, update_book, delete_book
from app.crud.author import get_author
from app.schemas.book import BookCreate, BookUpdate, Book
from app.models.user import User


class BookService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_book(self, book_data: BookCreate, user: User) -> Book:
        """Create a book with business logic validation."""
        # Business logic: check if user can create books
        if not user:
            raise ValueError("User is required to create a book")
        
        # Business logic: validate book data
        if book_data.publication_year > 2024:
            raise ValueError("Publication year cannot be in the future")
        
        # Business logic: check if author exists and belongs to user
        if book_data.author_id:
            author = get_author(self.db, book_data.author_id, user.id)
            if not author:
                raise ValueError("Author not found")
        
        return create_book(self.db, book_data, user.id)
    
    def get_user_books(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Book]:
        """Get books for user with pagination."""
        return get_books(self.db, user_id, skip, limit)
    
    def get_user_book(self, user_id: int, book_id: int) -> Optional[Book]:
        """Get a specific book for user."""
        book = get_book(self.db, book_id, user_id)
        if book and book.user_id == user_id:
            return book
        return None
    
    def update_user_book(self, user_id: int, book_id: int, book_data: BookUpdate) -> Optional[Book]:
        """Update a book for user with business logic validation."""
        # Check if book exists and belongs to user
        book = self.get_user_book(user_id, book_id)
        if not book:
            return None
        
        # Business logic: validate publication year
        if book_data.publication_year and book_data.publication_year > 2024:
            raise ValueError("Publication year cannot be in the future")
        
        # Business logic: check if author exists and belongs to user
        if book_data.author_id:
            author = get_author(self.db, book_data.author_id, user_id)
            if not author:
                raise ValueError("Author not found")
        
        return update_book(self.db, book_id, book_data, user_id)
    
    def delete_user_book(self, user_id: int, book_id: int) -> bool:
        """Delete a book for user."""
        # Check if book exists and belongs to user
        book = self.get_user_book(user_id, book_id)
        if not book:
            return False
        
        return delete_book(self.db, book_id, user_id)
    
    def search_books(self, user_id: int, query: str, skip: int = 0, limit: int = 100) -> List[Book]:
        """Search books by title or description for user."""
        # Business logic: validate search query
        if not query or len(query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters long")
        
        # Get all books and filter by search query
        books = get_books(self.db, user_id, skip, limit)
        query_lower = query.lower()
        
        return [
            book for book in books 
            if query_lower in book.title.lower() or 
               (book.description and query_lower in book.description.lower())
        ]
