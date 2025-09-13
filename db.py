from fastapi import Depends
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

from config import DB_URL


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DB_URL, echo=True)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
