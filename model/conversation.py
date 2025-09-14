from pydantic import BeforeValidator, Field, field_serializer
from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, TYPE_CHECKING

from .base import IdBase, IdBaseModel
from .relationships import conversation_user_table

if TYPE_CHECKING:
    from .article import ArticleModel
    from .message import MessageModel
    from .user import UserModel


class ConversationModel(IdBase):
    __tablename__ = "conversations"

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    event: Mapped[Optional["ArticleModel"]] = relationship(
        back_populates="event_conversation",
        lazy=True,
    )

    messages: Mapped[list["MessageModel"]] = relationship(
        back_populates="conversation",
        lazy=True,
    )

    users: Mapped[list["UserModel"]] = relationship(
        secondary=conversation_user_table,
        lazy=True,
    )
