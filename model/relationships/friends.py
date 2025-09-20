from sqlalchemy import Column, ForeignKey, Table

from db import Base

friend_table = Table(
    "user_friends",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), index=True),
    Column("friend_id", ForeignKey("users.id"), index=True),
)
