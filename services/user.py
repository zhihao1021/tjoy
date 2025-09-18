from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Union

from db import get_session
from exceptions.user_not_found import USER_NOT_FOUND
from model import UserModel
from model.view import UserInfo
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
