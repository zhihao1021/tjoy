from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Literal, Optional

from db import get_session
from exceptions.article import CREATE_ARTICLE_ERROR
from model import ArticleModel
from schemas.article import ArticleCreate
from snowflake import SnowflakeGenerator

from .category import check_category_exists

id_generator = SnowflakeGenerator()


async def create_article(
    author_id: int,
    data: ArticleCreate,
    session: Optional[AsyncSession],
    commit: bool = True
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
            id=id_generator.next_id(),
            author_id=author_id,
            category_id=int(data.category_id),
            **data.model_dump(exclude={"category_id"})
        )

        if commit:
            session.add(article)

            try:
                await session.commit()
            except:
                await session.rollback()
                raise CREATE_ARTICLE_ERROR

            await session.refresh(article)

        return article


async def get_all_articles(
    type: Optional[Literal["follow", "event"]] = None,
    session: Optional[AsyncSession] = None,
    fetch_author: bool = False,
    fetch_category: bool = False,
) -> list[ArticleModel]:
    async with get_session(session) as session:
        stat = select(ArticleModel)
        if type == "follow":
            stat = stat.where(ArticleModel.is_event == False)
        elif type == "event":
            stat = stat.where(ArticleModel.is_event == True)

        if fetch_author:
            stat = stat.options(joinedload(ArticleModel.author))
        if fetch_category:
            stat = stat.options(joinedload(ArticleModel.category))

        result = await session.execute(stat)

        return list(result.scalars().all())


async def get_article_by_id(
    article_id: int,
    session: Optional[AsyncSession] = None,
    fetch_author: bool = False,
    fetch_category: bool = False,
) -> ArticleModel:
    async with get_session(session) as session:
        options = []
        if fetch_author:
            options.append(joinedload(ArticleModel.author))
        if fetch_category:
            options.append(joinedload(ArticleModel.category))

        article = await session.get(
            ArticleModel,
            article_id,
            options=options
        )

        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found."
            )

        return article
