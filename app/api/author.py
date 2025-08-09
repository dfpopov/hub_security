from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.crud.author import get_author, get_authors, create_author, update_author, delete_author
from app.schemas.author import Author, AuthorCreate, AuthorUpdate

router = APIRouter()


@router.get("/", response_model=List[Author])
def read_authors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all authors for the current user."""
    authors = get_authors(db, user_id=current_user.id, skip=skip, limit=limit)
    return authors


@router.post("/", response_model=Author)
def create_new_author(
    author: AuthorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new author for the current user."""
    return create_author(db=db, author=author, user_id=current_user.id)


@router.get("/{author_id}", response_model=Author)
def read_author(
    author_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific author by ID."""
    author = get_author(db, author_id=author_id, user_id=current_user.id)
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    return author


@router.put("/{author_id}", response_model=Author)
def update_existing_author(
    author_id: int,
    author: AuthorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing author."""
    db_author = update_author(db, author_id=author_id, author=author, user_id=current_user.id)
    if db_author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    return db_author


@router.delete("/{author_id}")
def delete_existing_author(
    author_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an author."""
    success = delete_author(db, author_id=author_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    return {"message": "Author deleted successfully"}
