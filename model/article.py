from pydantic import Field
from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, TYPE_CHECKING

from .base import IdBase, IdBaseModel
from .relationships import interest_table, join_event_table

if TYPE_CHECKING:
    from .category import Category, CategoryModel
    from .conversation import Conversation, ConversationModel
    from .comment import Comment, CommentModel
    from .user import User, UserModel


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
    event_week_day: Mapped[Optional[int]] = mapped_column(
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


class Article(IdBaseModel[ArticleModel]):
    author_id: int = Field(
        title="Author ID",
        description="ID of the user who authored the article.",
    )
    author: "User" = Field(
        title="Author",
        description="The user who authored the article.",
    )
    author_visibility: int = Field(
        title="Author Visibility",
        description="Visibility level of the author's information.",
        ge=0,
        le=3,
        examples=[0, 1, 2, 3],
    )

    category_id: Optional[int] = Field(
        default=None,
        title="Category ID",
        description="ID of the category the article belongs to.",
    )
    category: Optional["Category"] = Field(
        default=None,
        title="Category",
        description="The category the article belongs to.",
    )

    title: str = Field(
        title="Title",
        description="The title of the article.",
        examples=["My First Article"]
    )
    content: str = Field(
        title="Content",
        description="The main content of the article.",
        examples=["This is the content of my first article."]
    )
    tags: str = Field(
        default="",
        title="Tags",
        description="Comma-separated tags associated with the article.",
        examples=["tag1,tag2,tag3"]
    )
    is_public: bool = Field(
        title="Is Public",
        description="Indicates whether the article is public.",
        examples=[True, False]
    )
    is_event: bool = Field(
        title="Is Event",
        description="Indicates whether the article is an event.",
        examples=[True, False]
    )
    evnet_week_day: Optional[int] = Field(
        default=None,
        title="Event Week Day",
        description="The day of the week the event occurs (0=Monday, 6=Sunday).",
        ge=0,
        le=6,
        examples=[0, 1, 2, 3, 4, 5, 6],
    )
    event_number_min: Optional[int] = Field(
        default=None,
        title="Event Number Min",
        description="Minimum number of participants for the event.",
        ge=1,
        examples=[1, 10, 50],
    )
    event_number_max: Optional[int] = Field(
        default=None,
        title="Event Number Max",
        description="Maximum number of participants for the event.",
        ge=1,
        examples=[10, 50, 100],
    )
    event_conversation_id: Optional[int] = Field(
        default=None,
        title="Event Conversation ID",
        description="ID of the conversation associated with the event.",
    )
    event_conversation: Optional["Conversation"] = Field(
        default=None,
        title="Event Conversation",
        description="The conversation associated with the event.",
    )

    comments: list["Comment"] = Field(
        default_factory=list,
        title="Comments",
        description="List of comments on the article.",
    )
    interest_users: list["User"] = Field(
        default_factory=list,
        title="Interest Users",
        description="List of users interested in the article.",
    )
    join_users: list["User"] = Field(
        default_factory=list,
        title="Join Users",
        description="List of users who have joined the event.",
    )
