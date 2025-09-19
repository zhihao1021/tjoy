from fastapi import APIRouter

from .category import router as category_router
from .user import router as user_router

ROUTER = APIRouter()

ROUTER.include_router(category_router)
ROUTER.include_router(user_router)
