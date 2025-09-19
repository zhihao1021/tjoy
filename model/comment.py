from pydantic import Field
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from .base import IdBase, IdBaseModel

if TYPE_CHECKING:
    from .article import Article, ArticleModel
    from .user import User, UserModel


class CommentModel(IdBase):
    __tablename__ = "comments"

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"),
        nullable=False,
        index=True
    )
    article: Mapped["ArticleModel"] = relationship(
        back_populates="comments",
        lazy=True,
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    author: Mapped["UserModel"] = relationship(
        back_populates="comments",
        lazy=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class Comment(IdBaseModel[CommentModel]):
    article_id: int = Field(
        title="Article ID",
        description="ID of the article the comment belongs to.",
    )
    article: "Article" = Field(
        title="Article",
        description="The article the comment belongs to.",
    )

    author_id: int = Field(
        title="Author ID",
        description="ID of the user who authored the comment.",
    )
    author: "User" = Field(
        title="Author",
        description="The user who authored the comment.",
    )

    content: str = Field(
        title="Content",
        description="The content of the comment.",
        examples=["Great article!", "I totally agree with this."],
    )
