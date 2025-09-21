from fastapi import Depends
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, Optional

from config import DB_URL


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DB_URL)  # , echo=True)


@asynccontextmanager
async def get_session(exists_session: Optional[AsyncSession] = None) -> AsyncGenerator[AsyncSession, None]:
    if exists_session is not None:
        yield exists_session
        return

    async with AsyncSession(engine) as session:
        yield session


# @asynccontextmanager
async def __get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(__get_session)]
