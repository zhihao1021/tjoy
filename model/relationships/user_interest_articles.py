from sqlalchemy import Column, ForeignKey, Table

from db import Base

interest_table = Table(
    "user_interest_articles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("article_id", ForeignKey("articles.id")),
)
