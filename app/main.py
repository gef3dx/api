import warnings
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.session import init_db
from app.utils.exceptions import AppException

# Suppress the deprecation warning from passlib about the crypt module
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module="passlib.utils.*",
    message="'crypt' is deprecated",
)


# Create FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup
    await init_db()
    yield
    # Shutdown (if needed)
    pass


app = FastAPI(
    title="FastAPI Backend",
    description="A FastAPI backend service with user authentication, profile management, and RBAC",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API router
app.include_router(api_router)


# Add exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Any, exc: AppException):
    """Handle application exceptions."""
    return {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        }
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the FastAPI Backend API"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/health/db")
async def database_health_check():
    """Database health check endpoint."""
    # This is a placeholder for actual database health check
    # In a real application, you would check database connectivity
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
