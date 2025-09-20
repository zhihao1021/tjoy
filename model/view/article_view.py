from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Self

from db import get_session

from .user_view import UserView
from ..article import ArticleModel
from ..category import CategoryModel
from ..relationships import interest_table, join_event_table


class ArticleView(BaseModel):
    author_id: Optional[str] = None
    author_name: str
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    title: str
    content: str
    tags: str
    is_event: bool
    event_week_day: Optional[int] = None
    event_number_min: Optional[int] = None
    event_number_max: Optional[int] = None
    event_conversation_id: Optional[str] = None
    interest_count: int
    join_count: int

    @classmethod
    async def from_model(
        cls,
        model: ArticleModel,
        session: Optional[AsyncSession] = None
    ) -> Self:
        auhtor_id = None
        author_name = ""
        if model.author_visibility == 0:
            author_name = "匿名"
        else:
            author = model.author
            auhtor_id = author.id
            if model.author_visibility == 0b10:
                author_name = author.department
            elif model.author_visibility == 0b01:
                author_name = author.display_name
            else:
                author_name = f"{author.department} {author.display_name}"

        async with get_session(session) as session:
            category = await session.get(
                CategoryModel,
                model.category_id
            ) if model.category_id else None

            interest_count = 0
            join_count = 0

            result = (await session.execute(
                select(
                    func.count(interest_table.c.user_id),
                    func.count(join_event_table.c.user_id),
                ).where(
                    interest_table.c.article_id == model.id,
                    join_event_table.c.article_id == model.id,
                )
            )).first()

            if result is None:
                interest_count = 0
                join_count = 0
            else:
                interest_count, join_count = result

        return cls(
            author_id=str(auhtor_id) if auhtor_id is not None else None,
            author_name=author_name,
            category_id=str(category.id) if category else None,
            category_name=category.name if category else None,
            title=model.title,
            content=model.content,
            tags=model.tags,
            is_event=model.is_event,
            event_week_day=model.event_week_day,
            event_number_min=model.event_number_min,
            event_number_max=model.event_number_max,
            event_conversation_id=str(
                model.event_conversation_id
            ) if model.event_conversation_id else None,
            interest_count=interest_count,
            join_count=join_count
        )
