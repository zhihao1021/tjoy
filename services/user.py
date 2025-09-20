from bcrypt import gensalt, hashpw
from sqlalchemy import and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Union

from db import get_session
from exceptions.user import (
    USER_NOT_FOUND,
    USER_UPDATE_FAILED,
)
from model import UserModel
from model.relationships import friend_table
from model.view import UserView
from schemas.user import UserUpdate
from snowflake import SnowflakeID


async def get_user_by_id(
    user_id: Union[int, SnowflakeID],
    session: Optional[AsyncSession] = None
) -> UserView:
    async with get_session(session) as session:
        result = await UserView.query_by(
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
    username: Union[int, SnowflakeID],
    session: Optional[AsyncSession] = None
) -> UserView:
    async with get_session(session) as session:
        result = await UserView.query_by(
            session,
            UserModel.username == username
        )

    if result is None:
        raise USER_NOT_FOUND

    return result


async def add_friend_by_id(
    user_id: Union[int, SnowflakeID],
    friend_id: Union[int, SnowflakeID],
    session: Optional[AsyncSession] = None
) -> None:
    if user_id == friend_id:
        raise USER_UPDATE_FAILED

    async with get_session(session) as session:
        friend_exists = await session.execute(
            friend_table.select().where(or_(
                and_(friend_table.c.user_id == user_id,
                     friend_table.c.friend_id == friend_id),
                and_(friend_table.c.user_id == friend_id,
                     friend_table.c.friend_id == user_id)
            ))
        )

        if friend_exists.first() is not None:
            raise USER_UPDATE_FAILED

        await session.execute(friend_table.insert().values(
            user_id=user_id,
            friend_id=friend_id
        ))

        try:
            await session.commit()
        except:
            await session.rollback()
            raise USER_UPDATE_FAILED


async def get_friends_by_user_id(
    user_id: Union[int, SnowflakeID],
    session: Optional[AsyncSession] = None
) -> list[UserView]:
    async with get_session(session) as session:
        result = await session.execute(
            friend_table.select().where(
                or_(
                    friend_table.c.user_id == user_id,
                    friend_table.c.friend_id == user_id
                )
            )
        )

        friends = []
        for row in result.fetchall():
            friend_id = row.friend_id if row.user_id == user_id else row.user_id
            friend = await UserView.query_by(
                session,
                UserModel.id == friend_id
            )
            if friend:
                friends.append(friend)

        return friends


async def check_is_friend(
    user_id: Union[int, SnowflakeID],
    friend_id: Union[int, SnowflakeID],
    session: Optional[AsyncSession] = None
) -> bool:
    if user_id == friend_id:
        return False

    async with get_session(session) as session:
        friend_exists = await session.execute(
            friend_table.select().where(or_(
                and_(friend_table.c.user_id == user_id,
                     friend_table.c.friend_id == friend_id),
                and_(friend_table.c.user_id == friend_id,
                     friend_table.c.friend_id == user_id)
            ))
        )

        return friend_exists.first() is not None
