from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Create engine with proper timeout configurations
engine = create_engine(
    settings.database_url,
    # Connection pool settings
    pool_timeout=settings.database_pool_timeout,  # Time to wait for connection from pool
    pool_recycle=3600,  # Recycle connections after 1 hour to avoid stale connections
    pool_pre_ping=True,  # Verify connections before use
    # Connection timeout settings
    connect_args={
        "connect_timeout": settings.database_connect_timeout,  # Connection timeout
        "options": f"-c statement_timeout={settings.database_command_timeout * 1000}"  # Query timeout in ms
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()