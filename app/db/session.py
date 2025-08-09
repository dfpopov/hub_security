from sqlalchemy.orm import Session
from app.db.base import SessionLocal


def get_db_session() -> Session:
    """Get a database session."""
    return SessionLocal()
