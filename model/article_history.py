from pydantic import BeforeValidator, Field, field_serializer
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Annotated, TYPE_CHECKING, Union

from .base import IdBase, IdBaseModel

if TYPE_CHECKING:
    from .article import ArticleModel
    from .user import UserModel


class ArticleHistoryModel(IdBase):
    __tablename__ = "article_histories"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"),
        nullable=False,
        index=True
    )
