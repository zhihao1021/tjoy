from fastapi import APIRouter, status

from auth import UserIdDep
from db import SessionDep
from exceptions.user import USER_NOT_FOUND
from model.view import UserView
from schemas.user import UserUpdate
from services.user import (
    get_user_by_id,
    get_user_by_username,
    update_user_by_id,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    path="",
    description="Get current user profile information.",
    status_code=status.HTTP_200_OK,
)
async def get_current(
    user_id: UserIdDep,
    session: SessionDep,
) -> UserView:
    return await get_user_by_id(
        user_id=user_id,
        session=session,
    )


@router.put(
    path="",
    description="Update current user profile information.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_current(
    user_id: UserIdDep,
    user_update: UserUpdate,
    session: SessionDep,
) -> None:
    await update_user_by_id(
        user_id=user_id,
        user_update=user_update,
        session=session
    )


@router.get(
    path="/by-id/{user_id}",
    description="Get user profile information by user ID.",
    status_code=status.HTTP_200_OK,
)
async def get_by_id(
    user_id: int,
    session: SessionDep,
) -> UserView:
    return await get_user_by_id(
        user_id=user_id,
        session=session,
    )


@router.get(
    path="/by-username/{username}",
    description="Get user profile information by username.",
    status_code=status.HTTP_200_OK,
)
async def get_by_username(
    username: str,
    session: SessionDep,
) -> UserView:
    return await get_by_username(
        username=username,
        session=session,
    )
