from pydantic import Field
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from .base import IdBase, IdBaseModel
from .relationships import follow_category_table

if TYPE_CHECKING:
    from .article import Article, ArticleModel
    from .user import User, UserModel


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
    )

    followers: Mapped[list["UserModel"]] = relationship(
        secondary=follow_category_table,
    )


class Category(IdBaseModel[CategoryModel]):
    name: str = Field(
        title="Category Name",
        description="The name of the category.",
        examples=["Technology", "Health", "Sports"],
    )
    articles: list["Article"] = Field(
        default_factory=list,
        title="Articles",
        description="List of articles under this category.",
    )

    followers: list["User"] = Field(
        default_factory=list,
        title="Followers",
        description="List of users following this category.",
    )
