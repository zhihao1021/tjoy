from pydantic import BeforeValidator, Field, field_serializer
from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, TYPE_CHECKING

from .base import IdBase, IdBaseModel

if TYPE_CHECKING:
    from .conversation import ConversationModel
    from .user import UserModel


class MessageModel(IdBase):
    __tablename__ = "messages"

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    author: Mapped["UserModel"] = relationship(
        lazy=True,
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False,
        index=True
    )
    conversation: Mapped["ConversationModel"] = relationship(
        back_populates="messages",
        lazy=True,
    )

    context: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
