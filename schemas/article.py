from pydantic import BaseModel

from typing import Optional


class ArticleCreate(BaseModel):
    author_visibility: int
    category_id: int
    title: str
    content: str
    tags: str
    is_public: bool
    is_event: bool
    event_week_day: Optional[int] = None
    event_number_min: Optional[int] = None
    event_number_max: Optional[int] = None
