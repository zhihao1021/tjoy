from pydantic import BeforeValidator, Field, field_serializer
from sqlalchemy import BigInteger, String, Text
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
    from .article import ArticleModel
    from .category import CategoryModel
    from .conversation import ConversationModel
    from .comment import CommentModel
    from .search_history import SearchHistoryModel

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

    password_hash: Mapped[str] = mapped_column(
        String(60),
        nullable=False
    )

    articles: Mapped[list["ArticleModel"]] = relationship(
        back_populates="author",
        lazy=True,
    )
    comments: Mapped[list["CommentModel"]] = relationship(
        back_populates="author",
        lazy=True,
    )

    interest_articles: Mapped[list["ArticleModel"]] = relationship(
        secondary=interest_table,
        lazy=True,
    )
    join_events: Mapped[list["ArticleModel"]] = relationship(
        secondary=join_event_table,
        lazy=True,
    )
    follow_categories: Mapped[list["CategoryModel"]] = relationship(
        secondary=follow_category_table,
        lazy=True,
    )
    conversations: Mapped[list["ConversationModel"]] = relationship(
        secondary=conversation_user_table,
        lazy=True,
    )
    search_histories: Mapped[list["SearchHistoryModel"]] = relationship(
        back_populates="user",
        lazy=True,
    )
    article_histories: Mapped[list["ArticleModel"]] = relationship(
        secondary="article_histories",
        lazy=True,
    )
    friends: Mapped[list["UserModel"]] = relationship(
        secondary=friend_table,
        primaryjoin=id == friend_table.c.user_id,
        secondaryjoin=id == friend_table.c.friend_id,
        lazy=True,
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
    password_hash: Annotated[Union[bytes, str], StrToBytesValidator] = Field(
        title="Password",
        description="The password for the user account.",
        examples=["strongpassword123"],
    )

    @field_serializer("password_hash")
    def serialize_password_hash(self, password_hash: Union[bytes, str], _info) -> str:
        if isinstance(password_hash, str):
            return password_hash
        return bytes(password_hash).decode("utf-8")
