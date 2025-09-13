from pydantic import BaseModel, BeforeValidator, Field, field_serializer
from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from typing import Annotated, Union

from db import Base
from snowflake import SnowflakeID

from .base import SQLIDModelBase

StrToBytesValidator = BeforeValidator(
    lambda v: v.encode("utf-8") if isinstance(v, str) else v
)


class UserModel(Base):
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
    password_hash: Mapped[str] = mapped_column(
        String(60),
        nullable=False
    )


class User(SQLIDModelBase[UserModel]):
    __model_type__ = UserModel

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
