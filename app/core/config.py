from pydantic_settings import BaseSettings
from typing import Optional


import secrets
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "mysql+pymysql://user:password@localhost:3306/book_collection"
    test_database_url: str = "mysql+pymysql://user:password@localhost:3306/book_collection_test"
    
    # JWT Configuration
    secret_key: Optional[str] = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Application
    debug: bool = True
    api_v1_str: str = "/api/v1"
    project_name: str = "Book Collection API"
    
    # CORS Configuration
    allowed_origins: list[str] = [
        "http://localhost:3000",  # Development
        "http://localhost:8080",  # Development
    ]
    
    # Production origins (set via environment)
    cors_origins: str = ""  # Comma-separated list
    
    # Database Pool Configuration
    db_pool_size: int = 20
    db_max_overflow: int = 30
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.secret_key:
            # Generate a secure key if not provided
            self.secret_key = secrets.token_urlsafe(32)
    
    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins:
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.allowed_origins
    
    @property
    def is_production(self) -> bool:
        return not self.debug
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
