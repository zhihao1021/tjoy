from fastapi import APIRouter

from .user import router as user_router

ROUTER = APIRouter()

ROUTER.include_router(user_router)
