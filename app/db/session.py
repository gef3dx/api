from typing import AsyncGenerator

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


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get a database session.

    Yields:
        AsyncSession: An async database session
    """
    async with AsyncSessionLocal() as session:
        yield session


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
