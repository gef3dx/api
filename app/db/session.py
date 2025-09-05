from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,  # type: ignore
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create sync engine and session factory for Celery tasks
sync_engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get a database session.

    Yields:
        AsyncSession: An async database session
    """
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_db():
    """
    Get a synchronous database session for use in Celery tasks.

    Returns:
        Session: A synchronous database session
    """
    return SyncSessionLocal()


async def init_db() -> None:
    """
    Initialize the database by creating all tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close the database connection.
    """
    await engine.dispose()
