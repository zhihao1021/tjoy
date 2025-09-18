from pydantic import BaseModel
from sqlalchemy import ColumnElement, select, Row
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Self, Union

from snowflake import SnowflakeID

from ..user import UserModel


class UserInfo(BaseModel):
    id: SnowflakeID
    username: str
    display_name: str
    gender: str
    department: str

    @classmethod
    def __cvt_from_results(cls, results: Row) -> Self:
        return cls(
            id=SnowflakeID(results[0]),
            username=results[1],
            display_name=results[2],
            gender=results[3],
            department=results[4]
        )

    @classmethod
    async def query_by(
        cls,
        session: AsyncSession,
        *criterion: ColumnElement,
    ) -> Optional[Self]:
        result = (await session.execute(select(
            UserModel.id,
            UserModel.username,
            UserModel.display_name,
            UserModel.gender,
            UserModel.department
        ).where(*criterion))).first()

        return None if result is None else \
            cls.__cvt_from_results(result)

    @classmethod
    async def query_all_by(
        cls,
        session: AsyncSession,
        *criterion: ColumnElement,
    ) -> Optional[list[Self]]:
        result = (await session.execute(select(
            UserModel.id,
            UserModel.username,
            UserModel.display_name,
            UserModel.gender,
            UserModel.department
        ).where(*criterion))).all()

        return None if result is None else [
            cls.__cvt_from_results(row) for row in result
        ]
