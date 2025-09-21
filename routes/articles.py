from fastapi import APIRouter, Body
from rabbitmq_service.sender import send_message_to_rabbitmq

from asyncio import gather
from typing import Annotated, Literal, Optional

from auth import UserIdDep
from db import SessionDep
from exceptions.article import CREATE_ARTICLE_ERROR
from model.view import ArticleView, CommentView
from schemas.article import ArticleCreate
from services.article import (
    create_article,
    get_all_articles,
    get_article_by_id,
)
from services.comment import (
    add_comment_by_article_id,
    get_comments_by_article_id
)

router = APIRouter(
    prefix="/articles",
    tags=["Articles"]
)


@router.get(
    path="",
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


@router.post(
    path="",
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

    if (article.is_event):
        await send_message_to_rabbitmq(str(article.id))

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

    return await gather(*[ArticleView.from_model(
        model=article,
        session=session
    ) for article in articles])


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


@router.put(
    path="/{article_id}",
    description="Update an existing article by its ID."
)
async def update_article(
    article_id: int,
    session: SessionDep
):
    pass


@router.get(
    path="/{article_id}/comments",
    description="Get comments for an article by its ID."
)
async def get_comments(
    article_id: int,
    session: SessionDep
) -> list[CommentView]:
    comments = await get_comments_by_article_id(
        article_id=article_id,
        session=session
    )

    return await gather(*[
        CommentView.from_model(model=comment, session=session)
        for comment in comments
    ])


@router.post(
    path="/{article_id}/comments",
    description="Add a comment to an article by its ID."
)
async def add_comment(
    user_id: UserIdDep,
    article_id: int,
    content: Annotated[str, Body(embed=True, min_length=1)],
    author_visibility: Annotated[int, Body(embed=True, ge=0, le=3)],
    session: SessionDep
) -> CommentView:
    comment = await add_comment_by_article_id(
        article_id=article_id,
        author_id=user_id,
        content=content,
        author_visibility=author_visibility,
    )

    return await CommentView.from_model(
        model=comment,
        session=session
    )
