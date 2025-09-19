from sqlalchemy import Table

from db import engine, Base

article_view = Table(
    "article_view",
    Base.metadata,
    autoload_with=engine.engine
)
