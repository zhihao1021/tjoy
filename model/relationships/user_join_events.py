from sqlalchemy import Column, ForeignKey, Table

from db import Base

join_event_table = Table(
    "user_join_events",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), index=True),
    Column("article_id", ForeignKey("articles.id"), index=True),
)
