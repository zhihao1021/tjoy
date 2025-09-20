from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Union

from db import get_session
from model import CategoryModel
from model.view import CategoryView
from snowflake import SnowflakeID


async def get_all_categories(
        session: Optional[AsyncSession] = None
) -> list[CategoryView]:
    async with get_session() as session:
        return await CategoryView.get_all(session)


async def check_category_exists(
    category_id: Union[int, str, SnowflakeID],
    session: Optional[AsyncSession] = None
) -> bool:
    if isinstance(category_id, SnowflakeID):
        category_id = category_id.value
    elif isinstance(category_id, str):
        category_id = int(category_id)

    async with get_session() as session:
        category = await session.execute(select(
            CategoryModel.id
        ).where(CategoryModel.id == category_id))

        return category is not None
