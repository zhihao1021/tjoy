from fastapi import Depends
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

from config import DB_URL

engine = create_async_engine(
    DB_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1800 
)
async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)




class Base(DeclarativeBase):
    pass


engine = create_async_engine(DB_URL, echo=True)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
