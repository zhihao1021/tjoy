from pydantic import BaseModel
from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Self

from snowflake import SnowflakeID

from ..category import CategoryModel


class CategoryView(BaseModel):
    id: SnowflakeID
    name: str

    @classmethod
    def __cvt_from_results(cls, results: Row) -> Self:
        return cls(
            id=SnowflakeID(results[0]),
            name=results[1]
        )

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession
    ) -> list[Self]:
        result = (await session.execute(select(
            CategoryModel.id,
            CategoryModel.name
        ))).all()

        return [cls.__cvt_from_results(row) for row in result]
