from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Self

from db import get_session

from .user_view import UserView
from ..article import ArticleModel
from ..category import CategoryModel
from ..relationships import interest_table, join_event_table
from ..user import UserModel


class ArticleView(BaseModel):
    id: str
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
        async with get_session(session) as session:
            author_id = None
            author_name = ""
            if model.author_visibility == 0:
                author_name = "匿名"
            else:
                try:
                    author = model.author
                except:
                    author = await session.get(
                        UserModel,
                        model.author_id
                    ) if model.author_id else None

                if author is None:
                    author_name = "未知用户"
                else:
                    if model.author_visibility == 0b10:
                        author_name = author.department
                    elif model.author_visibility == 0b01:
                        author_id = model.author_id
                        author_name = author.display_name
                    else:
                        author_id = model.author_id
                        author_name = f"{author.department} {author.display_name}"

            category_id = model.category_id
            category_name = None
            try:
                if model.category:
                    category_name = model.category.name
            except:
                category = await session.get(
                    CategoryModel,
                    model.category_id
                ) if model.category_id else None

                if category:
                    category_name = category.name

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
            id=str(model.id),
            author_id=str(author_id) if author_id is not None else None,
            author_name=author_name,
            category_id=str(category_id) if category_id else None,
            category_name=category_name,
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
