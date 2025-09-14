from pydantic import BeforeValidator, Field, field_serializer
from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, TYPE_CHECKING

from .base import IdBase, IdBaseModel

if TYPE_CHECKING:
    from .article import ArticleModel
    from .user import UserModel


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
