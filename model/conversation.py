from pydantic import Field
from sqlalchemy import Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, TYPE_CHECKING

from .base import IdBase, IdBaseModel
from .relationships import conversation_user_table

if TYPE_CHECKING:
    from .article import Article, ArticleModel
    from .message import Message, MessageModel
    from .user import User, UserModel


class ConversationModel(IdBase):
    __tablename__ = "conversations"

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_private: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    event: Mapped[Optional["ArticleModel"]] = relationship(
        back_populates="event_conversation",
    )

    messages: Mapped[list["MessageModel"]] = relationship(
        back_populates="conversation",
    )

    users: Mapped[list["UserModel"]] = relationship(
        secondary=conversation_user_table,
    )


class Conversation(IdBaseModel[ConversationModel]):
    title: str = Field(
        title="Conversation Title",
        description="The title of the conversation.",
    )

    is_private: bool = Field(
        default=False,
        title="Is Private",
        description="Indicates if the conversation is private.",
    )

    event: Optional["Article"] = Field(
        default=None,
        title="Event",
        description="The event associated with this conversation, if any.",
    )

    messages: list["Message"] = Field(
        default_factory=list,
        title="Messages",
        description="List of messages in this conversation.",
    )

    users: list["User"] = Field(
        default_factory=list,
        title="Users",
        description="List of users participating in this conversation.",
    )
