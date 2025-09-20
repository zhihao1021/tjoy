from fastapi import APIRouter

from .articles import router as articles_router
from .category import router as category_router
from .friends import router as friends_router
from .user import router as user_router

ROUTER = APIRouter()

ROUTER.include_router(articles_router)
ROUTER.include_router(category_router)
ROUTER.include_router(friends_router)
ROUTER.include_router(user_router)
