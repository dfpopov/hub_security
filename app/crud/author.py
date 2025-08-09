from sqlalchemy.orm import Session
from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorUpdate


def get_author(db: Session, author_id: int, user_id: int) -> Author:
    """Get author by ID for a specific user."""
    return db.query(Author).filter(Author.id == author_id, Author.user_id == user_id).first()


def get_authors(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all authors for a specific user with pagination."""
    return db.query(Author).filter(Author.user_id == user_id).offset(skip).limit(limit).all()


def create_author(db: Session, author: AuthorCreate, user_id: int) -> Author:
    """Create a new author for a specific user."""
    db_author = Author(**author.model_dump(), user_id=user_id)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


def update_author(db: Session, author_id: int, author: AuthorUpdate, user_id: int) -> Author:
    """Update an author for a specific user."""
    db_author = get_author(db, author_id, user_id)
    if not db_author:
        return None
    
    update_data = author.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_author, field, value)
    
    db.commit()
    db.refresh(db_author)
    return db_author


def delete_author(db: Session, author_id: int, user_id: int) -> bool:
    """Delete an author for a specific user."""
    db_author = get_author(db, author_id, user_id)
    if not db_author:
        return False
    
    db.delete(db_author)
    db.commit()
    return True


def get_author_by_name(db: Session, name: str, user_id: int) -> Author:
    """Get author by name for a specific user."""
    return db.query(Author).filter(Author.name == name, Author.user_id == user_id).first()
