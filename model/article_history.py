from pydantic import Field
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import IdBase, IdBaseModel


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


class ArticleHistory(IdBaseModel[ArticleHistoryModel]):
    user_id: int = Field(
        title="User ID",
        description="ID of the user who viewed the article.",
    )
    article_id: int = Field(
        title="Article ID",
        description="ID of the article that was viewed.",
    )
