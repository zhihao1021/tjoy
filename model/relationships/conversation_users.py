from sqlalchemy import Column, ForeignKey, Table

from db import Base

conversation_user_table = Table(
    "conversation_users",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), index=True),
    Column("conversations_id", ForeignKey("conversations.id"), index=True),
)
