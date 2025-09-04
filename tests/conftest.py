import os
import sys
import warnings

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import all models to register them with Base metadata

from app.core.config import settings
from app.db.base import Base

# Override database URL for testing
settings.DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Suppress the deprecation warning from passlib about the crypt module
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module="passlib.utils.*",
    message="'crypt' is deprecated",
)


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
    yield engine
    # Properly await the dispose coroutine
    # This will be handled in the event loop


@pytest.fixture(scope="session")
async def create_tables(engine):
    """Create test database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def clear_database(engine, create_tables):
    """Clear database tables before each test."""
    # Make sure tables are created
    _ = create_tables

    try:
        async with engine.begin() as conn:
            # Get all table names
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(text(f"DELETE FROM {table.name}"))
        yield
    except Exception:
        # If there's an error (e.g., tables don't exist yet), just yield
        yield


@pytest.fixture
async def db_session(engine, create_tables):
    """Create a database session for testing."""
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    session = async_session_factory()
    try:
        yield session
    finally:
        # Rollback any changes made during the test
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with database session."""
    from fastapi.testclient import TestClient

    # Override the database dependency
    from app.db.session import get_db
    from app.main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
