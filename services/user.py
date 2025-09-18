from bcrypt import gensalt, hashpw
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Union

from db import get_session
from exceptions.user import (
    USER_NOT_FOUND,
    USER_UPDATE_FAILED,
)
from model import UserModel
from model.view import UserInfo
from schemas.user import UserUpdate
from snowflake import SnowflakeID


async def get_user_by_id(
    user_id: Union[int, SnowflakeID],
    session: Optional[AsyncSession] = None
) -> UserInfo:
    async with get_session(session) as session:
        result = await UserInfo.query_by(
            session,
            UserModel.id == user_id
        )

    if result is None:
        raise USER_NOT_FOUND

    return result


async def update_user_by_id(
    user_id: Union[int, SnowflakeID],
    user_update: UserUpdate,
    session: Optional[AsyncSession] = None
) -> None:
    async with get_session(session) as session:
        update_data = user_update.model_dump(
            exclude={"password"},
            exclude_none=True
        )
        if user_update.password is not None:
            salt = gensalt()
            hashed_password = hashpw(
                user_update.password.encode("utf-8"),
                salt
            )
            update_data["password_hash"] = hashed_password

        await session.execute(
            update(UserModel).
            where(UserModel.id == user_id).
            values(**update_data)
        )

        try:
            await session.commit()
        except:
            await session.rollback()
            raise USER_UPDATE_FAILED


async def get_user_by_username(
    username: str,
    session: Optional[AsyncSession] = None
) -> UserInfo:
    async with get_session(session) as session:
        result = await UserInfo.query_by(
            session,
            UserModel.username == username
        )

    if result is None:
        raise USER_NOT_FOUND

    return result
