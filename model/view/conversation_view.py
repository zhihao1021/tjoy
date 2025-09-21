from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Self

from db import get_session
from model import ConversationModel

from .article_view import ArticleView
from .message_view import MessageView
from .user_view import UserView
from ..article import ArticleModel
from ..message import MessageModel
from ..relationships import conversation_user_table
from ..user import UserModel


class ConversationView(BaseModel):
    id: str
    title: str
    is_private: bool
    event: Optional[ArticleView] = None
    users: list[UserView]
    latest_message: Optional[MessageView] = None

    @classmethod
    async def from_model(
        cls,
        model: ConversationModel,
        session: Optional[AsyncSession] = None
    ) -> Self:
        async with get_session(session) as session:
            try:
                users = [
                    UserView.from_model(user)
                    for user in model.users
                ]
            except:
                users = [
                    UserView.from_model(user)
                    for user in (await session.execute(select(
                        UserModel
                    ).join(
                        conversation_user_table,
                        conversation_user_table.c.conversations_id == model.id
                    ).where(
                        UserModel.id == conversation_user_table.c.user_id
                    ))).scalars().all()
                ]

            event = None
            try:
                if model.event is not None:
                    event = await ArticleView.from_model(
                        model.event,
                        session
                    )
            except:
                result = (await session.execute(select(
                    ArticleModel
                ).options(
                    joinedload(ArticleModel.author),
                    joinedload(ArticleModel.category),
                ).where(
                    ArticleModel.event_conversation_id == model.id
                ))).scalar()

                if result is not None:
                    event = await ArticleView.from_model(
                        result,
                        session=session
                    )

            latest_message = (await session.execute(select(
                MessageModel
            ).where(
                MessageModel.conversation_id == model.id
            ).order_by(
                MessageModel.id.desc()
            ).limit(1))).scalar()

            latest_message = MessageView.from_model(
                model=latest_message,
            ) if latest_message else None

            return cls(
                id=str(model.id),
                title=model.title,
                is_private=model.is_private,
                event=event,
                users=users,
                latest_message=latest_message
            )
