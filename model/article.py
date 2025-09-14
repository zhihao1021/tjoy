from pydantic import BeforeValidator, Field, field_serializer
from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Literal, Optional, TYPE_CHECKING

from .base import IdBase, IdBaseModel
from .relationships import interest_table, join_event_table

if TYPE_CHECKING:
    from .category import CategoryModel
    from .conversation import ConversationModel
    from .comment import CommentModel
    from .user import UserModel


class ArticleModel(IdBase):
    __tablename__ = "articles"

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    author: Mapped["UserModel"] = relationship(
        back_populates="articles",
        lazy=True,
    )
    author_visibility: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
        index=True
    )
    category: Mapped[Optional["CategoryModel"]] = relationship(
        back_populates="articles",
        lazy=True,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    tags: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    is_event: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    evnet_week_day: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    event_number_min: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    event_number_max: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    event_conversation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=True,
        index=True
    )
    event_conversation: Mapped[Optional["ConversationModel"]] = relationship(
        back_populates="event",
        lazy=True,
    )

    comments: Mapped[list["CommentModel"]] = relationship(
        back_populates="article",
        lazy=True,
    )
    interest_users: Mapped[list["UserModel"]] = relationship(
        secondary=interest_table,
        lazy=True,
    )
    join_users: Mapped[list["UserModel"]] = relationship(
        secondary=join_event_table,
        lazy=True,
    )
