from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Literal, Optional

from db import get_session
from model import Article, ArticleModel
from model.view import ArticleView
from schemas.article import ArticleCreate

from .category import check_category_exists


async def create_article(
    author_id: int,
    data: ArticleCreate,
    session: Optional[AsyncSession]
) -> ArticleModel:
    async with get_session(session) as session:
        category_exists = await check_category_exists(
            category_id=data.category_id,
            session=session
        )

        if not category_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category does not exist."
            )

        article = ArticleModel(
            author_id=author_id,
            category_id=int(data.category_id),
            **data.model_dump(exclude={"category_id"})
        )

        session.add(article)

        try:
            await session.commit()
        except:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create article."
            )

        await session.refresh(article)

        return article


async def get_all_articles(
    type: Optional[Literal["follow", "event"]] = None,
    session: Optional[AsyncSession] = None
) -> list[ArticleModel]:
    async with get_session(session) as session:
        stat = select(ArticleModel)
        if type == "follow":
            stat = stat.where(ArticleModel.is_event == False)
        elif type == "event":
            stat = stat.where(ArticleModel.is_event == True)

        result = await session.execute(stat)

        return list(result.scalars().all())


async def get_article_by_id(
    article_id: int,
    session: Optional[AsyncSession] = None
) -> ArticleModel:
    async with get_session(session) as session:
        article = await session.get(ArticleModel, article_id)

        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found."
            )

        return article
