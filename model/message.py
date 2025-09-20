from pydantic import Field
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from .base import IdBase, IdBaseModel

if TYPE_CHECKING:
    from .conversation import Conversation, ConversationModel
    from .user import User, UserModel


class MessageModel(IdBase):
    __tablename__ = "messages"

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    author: Mapped["UserModel"] = relationship()

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False,
        index=True
    )
    conversation: Mapped["ConversationModel"] = relationship(
        back_populates="messages",
    )

    context: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class Message(IdBaseModel[MessageModel]):
    author_id: int = Field(
        title="Author ID",
        description="ID of the user who authored the message.",
    )
    author: "User" = Field(
        title="Author",
        description="The user who authored the message.",
    )
    conversation_id: int = Field(
        title="Conversation ID",
        description="ID of the conversation the message belongs to.",
    )
    conversation: "Conversation" = Field(
        title="Conversation",
        description="The conversation the message belongs to.",
    )

    context: str = Field(
        title="Message Content",
        description="The content of the message.",
    )
