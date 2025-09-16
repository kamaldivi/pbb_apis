from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    # Database configuration
    database_url: Optional[str] = None
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "pure_bhakti_vault"
    database_user: str = "postgres"
    database_password: str = "postgres"

    # Database connection timeout settings (in seconds)
    database_connect_timeout: int = 30
    database_command_timeout: int = 60
    database_pool_timeout: int = 30

    # Legacy fields for backwards compatibility
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Handle legacy environment variables
        if self.db_host:
            self.database_host = self.db_host
        if self.db_port:
            self.database_port = self.db_port
        if self.db_name:
            self.database_name = self.db_name
        if self.db_user:
            self.database_user = self.db_user
        if self.db_password:
            self.database_password = self.db_password

        # Build database_url if not provided
        if not self.database_url:
            self.database_url = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"


@lru_cache()
def get_settings():
    return Settings()