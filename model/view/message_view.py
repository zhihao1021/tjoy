from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, Self

from db import get_session
from exceptions.user import USER_NOT_FOUND

from .user_view import UserView
from ..message import MessageModel
from ..user import UserModel


class MessageView(BaseModel):
    id: str
    author_id: str
    conversation_id: str
    context: str
    translated_context: str

    @classmethod
    def from_model(
        cls,
        model: MessageModel,
    ) -> Self:
        return cls(
            id=str(model.id),
            author_id=str(model.author_id),
            conversation_id=str(model.conversation_id),
            context=model.context,
            translated_context=model.translated_context,
        )
