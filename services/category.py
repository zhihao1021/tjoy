from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional

from db import get_session
from model.view import CategoryView


async def get_all_categories(
        session: Optional[AsyncSession] = None
) -> list[CategoryView]:
    async with get_session() as session:
        return await CategoryView.get_all(session)
