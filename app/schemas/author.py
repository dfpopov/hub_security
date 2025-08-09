from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, description="Author name is required")
    biography: str = Field(..., min_length=1, description="Author biography is required")


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    biography: Optional[str] = None


class AuthorInDB(AuthorBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class Author(AuthorInDB):
    pass


class AuthorWithBooks(Author):
    books: List["Book"] = []


# Import at the end to avoid circular imports
from app.schemas.book import Book
