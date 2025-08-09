from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BookBase(BaseModel):
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = None


class BookCreate(BookBase):
    author_id: int


class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    author_id: Optional[int] = None


class BookInDB(BookBase):
    id: int
    author_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class Book(BookInDB):
    pass


class BookWithAuthor(Book):
    author: "Author"


# Import at the end to avoid circular imports
from app.schemas.author import Author
