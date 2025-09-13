from pydantic import BaseModel, Field
from sqlalchemy.orm import DeclarativeBase

from typing import Generic, Optional, Type, TypeVar

from snowflake import SnowflakeID

T = TypeVar("T", bound=DeclarativeBase)


class SQLIDModelBase(BaseModel, Generic[T]):
    __model_type__: Optional[Type[T]] = None

    id: SnowflakeID = Field(
        title="ID",
        description="The unique identifier",
    )

    def to_model(self) -> T:
        def generate(v: Type[T]) -> T:
            return v(123)

        if self.__model_type__ is None:
            raise ValueError("Model type is not defined.")

        return self.__model_type__(
            id=self.id.value,
            **self.model_dump(exclude={"id"})
        )
