from fastapi import APIRouter, Query
from rabbitmq_service.sender import send_message_to_rabbitmq

from asyncio import gather
from typing import Annotated, Literal, Optional

from auth import UserIdDep
from db import SessionDep
from exceptions.article import CREATE_ARTICLE_ERROR
from model.view import ArticleView
from schemas.article import ArticleCreate
from services.article import (
    create_article,
    get_all_articles,
    get_article_by_id,
)

router = APIRouter(
    prefix="/articles",
    tags=["Articles"]
)


@router.get(
    path="/",
    description="List articles with optional filtering by type."
)
async def list_articles(
    session: SessionDep,
    type: Optional[Literal[
        "follow", "event"
    ]] = None,
) -> list[ArticleView]:
    return await gather(*[
        ArticleView.from_model(model=article, session=session)
        for article in await get_all_articles(
            type=type,
            session=session,
            fetch_author=True,
            fetch_category=True
        )
    ])


@router.get(
    path="/{article_id}",
    description="Get a specific article by its ID."
)
async def get_article(
    article_id: int,
    session: SessionDep
) -> ArticleView:
    article = await get_article_by_id(
        article_id=article_id,
        session=session,
        fetch_author=True,
        fetch_category=True,
    )

    return await ArticleView.from_model(
        model=article,
        session=session
    )


@router.post(
    path="/",
    description="Create a new article."
)
async def create(
    user_id: UserIdDep,
    data: ArticleCreate,
    session: SessionDep
) -> ArticleView:
    article = await create_article(
        author_id=user_id,
        data=data,
        session=session
    )

    # TODO: Check Activity or pure Article
    # TODO: send activity_id to RabbitMQ
    # await send_message_to_rabbitmq(insert_activity_id_here)

    return await ArticleView.from_model(
        model=article,
        session=session
    )


@router.post(
    path="/bulk",
    description="Create articles in once"
)
async def create_bulk(
    user_id: UserIdDep,
    data: list[ArticleCreate],
    session: SessionDep
) -> list[ArticleView]:
    articles = await gather(*[create_article(
        author_id=user_id,
        data=d,
        session=session
    ) for d in data])

    try:
        await session.commit()

        await gather(*[
            session.refresh(article)
            for article in articles
        ])
    except:
        await session.rollback()
        raise CREATE_ARTICLE_ERROR

    # TODO: Check Activity or pure Article
    # TODO: send activity_id to RabbitMQ
    # await send_message_to_rabbitmq(insert_activity_id_here)

    return await gather(*[ArticleView.from_model(
        model=article,
        session=session
    ) for article in articles])


@router.put(
    path="/{article_id}",
    description="Update an existing article by its ID."
)
async def update_article(article_id: int):
    pass


@router.post(
    path="/{article_id}/comment",
    description="Add a comment to an article by its ID."
)
async def add_comment(article_id: int):
    pass
