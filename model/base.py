from pydantic import BaseModel, Field
from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from typing import cast, Generic, TypeVar
from types import get_original_bases

from db import Base
from snowflake import SnowflakeID

T = TypeVar("T", bound=DeclarativeBase)
U = TypeVar("U", bound="IdBase")


class IdBase(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        unique=True,
        nullable=False
    )


class SQLBaseModel(BaseModel, Generic[T]):
    def to_model(self) -> T:
        sql_model = None

        for base in get_original_bases(self.__class__):
            if not issubclass(base, IdBaseModel):
                continue

            args = base.__pydantic_generic_metadata__.get("args")
            if not args or len(args) < 1:
                raise ValueError("Generic type arguments not found.")
            if not issubclass(args[0], DeclarativeBase):
                raise ValueError(
                    "Generic type argument is not a SQLAlchemy model.")

            sql_model = args[0]

        if sql_model is None:
            raise ValueError("SQLAlchemy model class not found.")

        if hasattr(self, "id"):
            if not issubclass(sql_model, IdBase):
                raise ValueError(
                    "The SQLAlchemy model does not have an 'id' field.")

            id_val = getattr(self, "id")
            model = sql_model(
                id=id_val.value if isinstance(id_val, SnowflakeID) else id_val,
                **self.model_dump(exclude={"id"})
            )
        else:
            model = sql_model(**self.model_dump())

        return cast(T, model)


class IdBaseModel(SQLBaseModel[U], Generic[U]):
    id: SnowflakeID = Field(
        title="ID",
        description="The unique identifier",
    )
