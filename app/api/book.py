from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.book_service import BookService
from app.schemas.book import Book, BookCreate, BookUpdate, PaginatedResponse
from app.core.rate_limiter import limiter, get_user_rate_limit_key

router = APIRouter()


def get_book_service(db: Session = Depends(get_db)) -> BookService:
    """Dependency to get book service."""
    return BookService(db)

@router.get("/", response_model=PaginatedResponse[Book])
@limiter.limit("30/minute", key_func=get_user_rate_limit_key)
def read_books(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    publication_year: Optional[int] = Query(None, description="Filter by publication year"),
    current_user: User = Depends(get_current_user),
    book_service: BookService = Depends(get_book_service)
):
    """Get all books for the current user with optional filtering and pagination."""
    from app.crud.book import get_books_with_pagination
    
    # Get books with pagination
    books, total = get_books_with_pagination(
        book_service.db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit,
        author_id=author_id,
        genre=genre,
        publication_year=publication_year
    )
    
    # Calculate pagination metadata
    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit
    has_next = skip + limit < total
    has_prev = skip > 0
    
    return PaginatedResponse(
        items=books,
        total=total,
        page=page,
        size=len(books),
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.post("/", response_model=Book)
def create_new_book(
    book: BookCreate,
    current_user: User = Depends(get_current_user),
    book_service: BookService = Depends(get_book_service)
):
    """Create a new book for the current user."""
    try:
        return book_service.create_book(book, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{book_id}", response_model=Book)
def read_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    book_service: BookService = Depends(get_book_service)
):
    """Get a specific book by ID."""
    book = book_service.get_user_book(current_user.id, book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book


@router.put("/{book_id}", response_model=Book)
def update_existing_book(
    book_id: int,
    book: BookUpdate,
    current_user: User = Depends(get_current_user),
    book_service: BookService = Depends(get_book_service)
):
    """Update an existing book."""
    try:
        db_book = book_service.update_user_book(current_user.id, book_id, book)
        if db_book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return db_book
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{book_id}")
def delete_existing_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    book_service: BookService = Depends(get_book_service)
):
    """Delete a book."""
    success = book_service.delete_user_book(current_user.id, book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return {"message": "Book deleted successfully"}
