from fastapi import APIRouter, Body

from typing import Annotated

from auth import UserIdDep
from db import SessionDep
from model.view import UserView
from services.user import (
    add_friend_by_id,
    check_is_friend,
    get_friends_by_user_id
)

router = APIRouter(
    prefix="/friends",
    tags=["Friends"]
)


@router.get(
    path="/",
    description="Get a list of friends for the authenticated user."
)
async def get_friends(
    user_id: UserIdDep,
    session: SessionDep,
) -> list[UserView]:
    return await get_friends_by_user_id(
        user_id=user_id,
        session=session
    )


@router.post(
    path="/add",
    description="Add a new friend by user ID."
)
async def add_friend(
    user_id: UserIdDep,
    friend_id: Annotated[int, Body(embed=True)],
    session: SessionDep,
) -> None:
    await add_friend_by_id(
        user_id=user_id,
        friend_id=friend_id,
        session=session
    )


@router.get(
    path="/check/{friend_id}",
    description="Check if a user is a friend by user ID.",
)
async def check_friend(
    user_id: UserIdDep,
    friend_id: int,
    session: SessionDep,
) -> bool:
    return await check_is_friend(
        user_id=user_id,
        friend_id=friend_id,
        session=session
    )
