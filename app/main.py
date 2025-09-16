from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.routes import router
from app.database import engine
from app.models.models import Base
from app.config import get_settings
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pure Bhakti Vault API",
    description="RESTful API for Pure Bhakti spiritual content including books, articles, lectures, and verses",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for multiple platforms
def get_cors_origins():
    """Get CORS origins based on environment"""
    # Development origins
    dev_origins = [
        "http://localhost:3000",     # React dev server
        "http://localhost:3001",     # Alternative React port
        "http://localhost:5173",     # Vite dev server
        "http://localhost:8080",     # Vue dev server
        "http://127.0.0.1:3000",     # Local React
        "https://localhost:3000",    # HTTPS React
    ]

    # Production origins
    prod_origins = [
        "https://www.purebhaktibase.com",
        "https://purebhaktibase.com",
        "https://api.purebhaktibase.com",
        "https://app.purebhaktibase.com",
    ]

    # Mobile app origins (for development)
    mobile_origins = [
        "http://localhost",          # React Native Metro
        "http://10.0.2.2:8081",     # Android emulator
        "http://192.168.1.100",     # Local network (update with your IP)
    ]

    # Custom origins from environment variable
    custom_origins = os.getenv("CORS_ORIGINS", "").split(",")
    custom_origins = [origin.strip() for origin in custom_origins if origin.strip()]

    # Combine all origins
    all_origins = dev_origins + prod_origins + mobile_origins + custom_origins

    # In development, allow all origins for testing
    if os.getenv("ENVIRONMENT", "development") == "development":
        return ["*"]

    return list(set(all_origins))  # Remove duplicates

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Support all methods
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-API-Key",
        "Cache-Control",
    ],
    expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"],  # Useful for pagination
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["Pure Bhakti Vault"])


@app.get("/")
def root():
    return {
        "message": "Welcome to Pure Bhakti Vault API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "pure-bhakti-apis"}