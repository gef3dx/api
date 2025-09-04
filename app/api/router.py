from fastapi import APIRouter

from app.domain.auth.router import router as auth_router
from app.domain.messages.router import router as messages_router
from app.domain.notifications.router import router as notifications_router
from app.domain.profiles.router import router as profiles_router
from app.domain.users.router import router as users_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all domain routers
api_router.include_router(auth_router)
api_router.include_router(messages_router)
api_router.include_router(notifications_router)
api_router.include_router(profiles_router)
api_router.include_router(users_router)

__all__ = ["api_router"]
