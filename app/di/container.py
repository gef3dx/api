from typing import AsyncGenerator

from dishka import Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.domain.auth.repository import AuthRepository
from app.domain.auth.service import AuthService
from app.domain.profiles.repository import ProfileRepository
from app.domain.profiles.service import ProfileService
from app.domain.users.repository import UserRepository
from app.domain.users.service import UserService


class DatabaseProvider(Provider):
    """Provider for database-related dependencies."""

    @provide(scope=Scope.REQUEST)
    def get_engine(self) -> AsyncEngine:
        """Provide database engine."""
        return create_async_engine(
            settings.DATABASE_URL, echo=settings.DEBUG, future=True
        )

    @provide(scope=Scope.REQUEST)
    def get_session_maker(self, engine: AsyncEngine) -> sessionmaker:
        """Provide session maker."""
        return sessionmaker(
            bind=engine,  # type: ignore
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_maker: sessionmaker
    ) -> AsyncGenerator[AsyncSession, None]:
        """Provide database session."""
        async with session_maker() as session:
            yield session


class RepositoryProvider(Provider):
    """Provider for repository dependencies."""

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: AsyncSession) -> UserRepository:
        """Provide user repository."""
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_profile_repository(self, session: AsyncSession) -> ProfileRepository:
        """Provide profile repository."""
        return ProfileRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_auth_repository(self, session: AsyncSession) -> AuthRepository:
        """Provide auth repository."""
        return AuthRepository(session)


class ServiceProvider(Provider):
    """Provider for service dependencies."""

    @provide(scope=Scope.REQUEST)
    def get_user_service(
        self, user_repo: UserRepository, profile_repo: ProfileRepository
    ) -> UserService:
        """Provide user service."""
        return UserService(user_repo, profile_repo)

    @provide(scope=Scope.REQUEST)
    def get_profile_service(self, profile_repo: ProfileRepository) -> ProfileService:
        """Provide profile service."""
        return ProfileService(profile_repo)

    @provide(scope=Scope.REQUEST)
    def get_auth_service(
        self,
        auth_repo: AuthRepository,
        user_repo: UserRepository,
        user_service: UserService,
    ) -> AuthService:
        """Provide auth service."""
        return AuthService(auth_repo, user_repo, user_service)


def create_container():
    """Create and configure the dependency injection container."""
    providers = [DatabaseProvider(), RepositoryProvider(), ServiceProvider()]
    return make_async_container(*providers)
