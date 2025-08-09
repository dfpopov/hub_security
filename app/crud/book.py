from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate
from app.crud.author import get_author
from typing import Tuple, List


def get_book(db: Session, book_id: int, user_id: int) -> Book:
    """Get book by ID for a specific user."""
    return db.query(Book).filter(Book.id == book_id, Book.user_id == user_id).first()


def get_books(db: Session, user_id: int, skip: int = 0, limit: int = 100, 
              author_id: int = None, genre: str = None, publication_year: int = None,
              include_author: bool = True) -> List[Book]:
    """Get all books for a specific user with optional filtering."""
    query = db.query(Book).filter(Book.user_id == user_id)
    
    # Eager loading to prevent N+1 queries
    if include_author:
        query = query.options(joinedload(Book.author))
    
    if author_id:
        query = query.filter(Book.author_id == author_id)
    if genre:
        query = query.filter(Book.genre == genre)
    if publication_year:
        query = query.filter(Book.publication_year == publication_year)
    
    return query.offset(skip).limit(limit).all()


def get_books_with_pagination(db: Session, user_id: int, skip: int = 0, limit: int = 100,
                             author_id: int = None, genre: str = None, publication_year: int = None,
                             include_author: bool = True) -> Tuple[List[Book], int]:
    """Get books with pagination and return total count."""
    # Build base query
    query = db.query(Book).filter(Book.user_id == user_id)
    
    # Apply filters
    if author_id:
        query = query.filter(Book.author_id == author_id)
    if genre:
        query = query.filter(Book.genre == genre)
    if publication_year:
        query = query.filter(Book.publication_year == publication_year)
    
    # Get total count
    total = query.count()
    
    # Apply eager loading and pagination
    if include_author:
        query = query.options(joinedload(Book.author))
    
    books = query.offset(skip).limit(limit).all()
    
    return books, total


def create_book(db: Session, book: BookCreate, user_id: int) -> Book:
    """Create a new book for a specific user."""
    # Verify that the author belongs to the user
    author = get_author(db, book.author_id, user_id)
    if not author:
        raise ValueError("Author not found or does not belong to user")
    
    db_book = Book(**book.model_dump(), user_id=user_id)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, book: BookUpdate, user_id: int) -> Book:
    """Update a book for a specific user."""
    db_book = get_book(db, book_id, user_id)
    if not db_book:
        return None
    
    update_data = book.model_dump(exclude_unset=True)
    
    # If author_id is being updated, verify it belongs to the user
    if "author_id" in update_data:
        author = get_author(db, update_data["author_id"], user_id)
        if not author:
            raise ValueError("Author not found or does not belong to user")
    
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int, user_id: int) -> bool:
    """Delete a book for a specific user."""
    db_book = get_book(db, book_id, user_id)
    if not db_book:
        return False
    
    db.delete(db_book)
    db.commit()
    return True


def get_book_by_title(db: Session, title: str, user_id: int) -> Book:
    """Get book by title for a specific user."""
    return db.query(Book).filter(Book.title == title, Book.user_id == user_id).first()
