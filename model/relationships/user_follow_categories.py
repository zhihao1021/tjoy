from sqlalchemy import Column, ForeignKey, Table

from db import Base

follow_category_table = Table(
    "user_follow_categories",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("category_id", ForeignKey("categories.id")),
)
