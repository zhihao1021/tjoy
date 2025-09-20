from pydantic import BaseModel
from sqlalchemy import ColumnElement, or_, Row, select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Self, Union

from snowflake import SnowflakeID

from ..user import UserModel
from ..relationships import friend_table


class UserView(BaseModel):
    id: SnowflakeID
    username: str
    display_name: str
    gender: str
    department: str
    onboarding_year: int
    onboarding_month: int
    onboarding_day: int
    interest: str

    @staticmethod
    def select_properties() -> Select:
        return select(
            UserModel.id,
            UserModel.username,
            UserModel.display_name,
            UserModel.gender,
            UserModel.department,
            UserModel.onboarding_year,
            UserModel.onboarding_month,
            UserModel.onboarding_day,
            UserModel.interest,
        )

    @classmethod
    def __cvt_from_results(cls, results: Row) -> Self:
        return cls(
            id=SnowflakeID(results[0]),
            username=results[1],
            display_name=results[2],
            gender=results[3],
            department=results[4],
            onboarding_year=results[5],
            onboarding_month=results[6],
            onboarding_day=results[7],
            interest=results[8],
        )

    @classmethod
    async def query_by(
        cls,
        session: AsyncSession,
        *criterion: ColumnElement,
    ) -> Optional[Self]:
        result = (await session.execute(
            cls.select_properties().where(*criterion)
        )).first()

        return None if result is None else \
            cls.__cvt_from_results(result)

    @classmethod
    async def query_all_by(
        cls,
        session: AsyncSession,
        *criterion: ColumnElement,
    ) -> list[Self]:
        result = (await session.execute(
            cls.select_properties().where(*criterion)
        )).all()

        return [] if result is None else [
            cls.__cvt_from_results(row) for row in result
        ]

    @classmethod
    async def get_friends(
        cls,
        user_id: Union[int, SnowflakeID],
        session: AsyncSession
    ) -> list[Self]:
        result = (await session.execute(cls.select_properties().where(
            or_(
                UserModel.id.in_(select(friend_table.c.user_id).where(
                    friend_table.c.friend_id == user_id
                )),
                UserModel.id.in_(select(friend_table.c.friend_id).where(
                    friend_table.c.user_id == user_id
                )),
            )
        ))).all()

        return [] if result is None else [
            cls.__cvt_from_results(row) for row in result
        ]
