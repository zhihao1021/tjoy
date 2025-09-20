from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Self

from db import get_session
from model import ConversationModel

from .article_view import ArticleView
from .user_view import UserView


class ConversationView(BaseModel):
    id: str
    title: str
    is_private: bool
    event: Optional[ArticleView] = None
    users: list[UserView]

    @classmethod
    async def from_model(
        cls,
        model: ConversationModel,
        session: Optional[AsyncSession] = None
    ) -> Self:
        async with get_session(session) as session:
            users = [
                UserView.from_model(user)
                for user in model.users
            ]

            event = None
            if model.event is not None:
                event = await ArticleView.from_model(model.event, session)

            return cls(
                id=str(model.id),
                title=model.title,
                is_private=model.is_private,
                event=event,
                users=users
            )
