from pydantic import BeforeValidator, Field, field_serializer
from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, TYPE_CHECKING

from .base import IdBase, IdBaseModel
from .relationships import follow_category_table

if TYPE_CHECKING:
    from .article import ArticleModel
    from .user import UserModel


class CategoryModel(IdBase):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True
    )
    articles: Mapped[list["ArticleModel"]] = relationship(
        back_populates="category",
        lazy=True,
    )

    followers: Mapped[list["UserModel"]] = relationship(
        secondary=follow_category_table,
        lazy=True,
    )
