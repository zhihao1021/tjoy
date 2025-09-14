from pydantic import BeforeValidator, Field, field_serializer
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Annotated, TYPE_CHECKING, Union

from .base import IdBase, IdBaseModel

if TYPE_CHECKING:
    from .user import UserModel


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
