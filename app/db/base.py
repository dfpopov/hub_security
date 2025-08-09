from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base_class import Base

# Import all models here so they are registered with SQLAlchemy
from app.models.user import User
from app.models.author import Author
from app.models.book import Book

# Create database engine with proper pooling
if "sqlite" in settings.database_url.lower():
    # SQLite configuration
    engine = create_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False}
    )
else:
    # MySQL configuration
    engine = create_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_pre_ping=True,
        pool_recycle=settings.db_pool_recycle,
        echo=settings.debug,
        # Additional safety settings
        connect_args={
            "charset": "utf8mb4",
            "autocommit": False,
        }
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
