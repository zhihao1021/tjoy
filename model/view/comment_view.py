from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Self

from db import get_session
from exceptions.user import USER_NOT_FOUND

from .user_view import UserView
from ..comment import CommentModel
from ..user import UserModel


class CommentView(BaseModel):
    id: str
    article_id: str
    author_id: Optional[str] = None
    author_name: str
    content: str

    @classmethod
    async def from_model(
        cls,
        model: CommentModel,
        session: Optional[AsyncSession] = None
    ) -> Self:
        async with get_session(session) as session:
            try:
                author = UserView.from_model(model=model.author)
            except:
                author_model = await session.get(
                    UserModel,
                    model.author_id
                )
                if author_model is None:
                    raise USER_NOT_FOUND

                author = UserView.from_model(model=author_model)

            author_id = None
            author_name = ""
            if model.author_visibility == 0:
                author_name = "匿名"
            else:
                if model.author_visibility == 0b10:
                    author_name = author.department
                elif model.author_visibility == 0b01:
                    author_id = model.author_id
                    author_name = author.display_name
                else:
                    author_id = model.author_id
                    author_name = f"{author.department} {author.display_name}"

            return cls(
                id=str(model.id),
                article_id=str(model.article_id),
                author_id=str(author_id) if author_id else None,
                author_name=author_name,
                content=model.content
            )
