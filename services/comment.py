from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from exceptions.comment import CREATE_COMMENT_ERROR
from model import CommentModel

from typing import Optional


async def get_comments_by_article_id(
    article_id: int,
    session: Optional[AsyncSession] = None,
    with_author: bool = False
) -> list[CommentModel]:
    async with get_session(session) as session:
        stat = select(CommentModel).where(
            CommentModel.article_id == article_id
        ).order_by(
            CommentModel.id.desc()
        )

        if with_author:
            stat = stat.options(
                joinedload(CommentModel.author)
            )

        comments = await session.execute(stat)
        comments = comments.scalars().all()

        return list(comments)


async def add_comment_by_article_id(
    article_id: int,
    author_id: int,
    content: str,
    author_visibility: int,
    session: Optional[AsyncSession] = None,
    commit: bool = True
) -> CommentModel:
    async with get_session(session) as session:
        comment = CommentModel(
            article_id=article_id,
            author_id=author_id,
            content=content,
            author_visibility=author_visibility
        )

        if commit:
            session.add(comment)

            try:
                await session.commit()
                await session.refresh(comment)
            except:
                from traceback import print_exc
                print_exc()

                await session.rollback()
                raise CREATE_COMMENT_ERROR

        return comment
