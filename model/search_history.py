from pydantic import Field
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from .base import IdBase, IdBaseModel

if TYPE_CHECKING:
    from .user import User, UserModel


class SearchHistoryModel(IdBase):
    __tablename__ = "search_histories"

    query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    user: Mapped["UserModel"] = relationship(
        back_populates="search_histories",
        lazy=True,
    )


class SearchHistory(IdBaseModel[SearchHistoryModel]):
    query: str = Field(
        title="Search Query",
        description="The search query string.",
    )

    user_id: int = Field(
        title="User ID",
        description="ID of the user who made the search.",
    )
    user: "User" = Field(
        title="User",
        description="The user who made the search.",
    )
