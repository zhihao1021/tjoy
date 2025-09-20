from pydantic import BeforeValidator, Field, field_serializer
from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Annotated, TYPE_CHECKING, Union

from .base import IdBase, IdBaseModel
from .relationships import (
    conversation_user_table,
    follow_category_table,
    interest_table,
    join_event_table,
    friend_table
)

if TYPE_CHECKING:
    from .article import Article, ArticleModel
    from .category import Category, CategoryModel
    from .conversation import Conversation, ConversationModel
    from .comment import Comment, CommentModel
    from .search_history import SearchHistory, SearchHistoryModel

StrToBytesValidator = BeforeValidator(
    lambda v: v.encode("utf-8") if isinstance(v, str) else v
)


class UserModel(IdBase):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        unique=True,
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True
    )
    display_name: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    gender: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    department: Mapped[str] = mapped_column(
        Text
    )
    onboarding_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    onboarding_month: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    onboarding_day: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    interest: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(60),
        nullable=False
    )

    articles: Mapped[list["ArticleModel"]] = relationship(
        back_populates="author",
    )
    comments: Mapped[list["CommentModel"]] = relationship(
        back_populates="author",
    )

    interest_articles: Mapped[list["ArticleModel"]] = relationship(
        secondary=interest_table,
    )
    join_events: Mapped[list["ArticleModel"]] = relationship(
        secondary=join_event_table,
    )
    follow_categories: Mapped[list["CategoryModel"]] = relationship(
        secondary=follow_category_table,
    )
    conversations: Mapped[list["ConversationModel"]] = relationship(
        secondary=conversation_user_table,
    )
    search_histories: Mapped[list["SearchHistoryModel"]] = relationship(
        back_populates="user",
    )
    article_histories: Mapped[list["ArticleModel"]] = relationship(
        secondary="article_histories",
    )
    friends: Mapped[list["UserModel"]] = relationship(
        secondary=friend_table,
        primaryjoin=id == friend_table.c.user_id,
        secondaryjoin=id == friend_table.c.friend_id,
    )


class User(IdBaseModel[UserModel]):
    username: str = Field(
        title="Username",
        description="The unique username of the user.",
        examples=["johndoe"]
    )
    display_name: str = Field(
        title="Display Name",
        description="The display name of the user.",
        examples=["John Doe"]
    )
    gender: str = Field(
        title="Gender",
        description="The gender of the user.",
        examples=["Female"]
    )
    department: str = Field(
        title="Department",
        description="The department the user belongs to.",
        examples=["Computer Science"]
    )
    onboarding_year: int = Field(
        title="Onboarding Year",
        description="The year the user joined the institution.",
        ge=1900,
        le=2100,
        examples=[2020, 2021, 2022],
    )
    onboarding_month: int = Field(
        title="Onboarding Month",
        description="The month the user joined the institution.",
        ge=1,
        le=12,
        examples=[1, 2, 3],
    )
    onboarding_day: int = Field(
        title="Onboarding Day",
        description="The day the user joined the institution.",
        ge=1,
        le=31,
        examples=[1, 15, 30],
    )
    interest: str = Field(
        default="",
        title="Interest",
        description="The user's interests.",
        examples=["Machine Learning, Data Science"]
    )

    password_hash: Annotated[Union[bytes, str], StrToBytesValidator] = Field(
        title="Password",
        description="The password for the user account.",
        examples=["strongpassword123"],
    )

    articles: list["Article"] = Field(
        default_factory=list,
        title="Articles",
        description="List of articles authored by the user.",
    )

    comments: list["Comment"] = Field(
        default_factory=list,
        title="Comments",
        description="List of comments authored by the user.",
    )

    interest_articles: list["Article"] = Field(
        default_factory=list,
        title="Interest Articles",
        description="List of articles the user is interested in.",
    )
    join_events: list["Article"] = Field(
        default_factory=list,
        title="Join Events",
        description="List of events the user has joined.",
    )
    follow_categories: list["Category"] = Field(
        default_factory=list,
        title="Follow Categories",
        description="List of categories the user follows.",
    )
    conversations: list["Conversation"] = Field(
        default_factory=list,
        title="Conversations",
        description="List of conversations the user is part of.",
    )
    search_histories: list["SearchHistory"] = Field(
        default_factory=list,
        title="Search Histories",
        description="List of search histories of the user.",
    )
    article_histories: list["Article"] = Field(
        default_factory=list,
        title="Article Histories",
        description="List of articles the user has viewed.",
    )
    friends: list["User"] = Field(
        default_factory=list,
        title="Friends",
        description="List of friends of the user.",
    )

    @field_serializer("password_hash")
    def serialize_password_hash(self, password_hash: Union[bytes, str], _info) -> str:
        if isinstance(password_hash, str):
            return password_hash
        return bytes(password_hash).decode("utf-8")
