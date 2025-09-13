from fastapi import APIRouter, Query

from typing import Annotated, Literal, Optional

router = APIRouter(
    prefix="/articles",
    tags=["Articles"]
)


@router.get(
    path="/",
    description="List articles with optional filtering by type."
)
async def list_articles(
    type: Annotated[Optional[Literal[
        "follow", "event"
    ]], Query(default=None)]
):
    pass


@router.get(
    path="/{article_id}",
    description="Get a specific article by its ID."
)
async def get_article(article_id: int):
    pass


@router.post(
    path="/",
    description="Create a new article."
)
async def create_article():
    pass


@router.put(
    path="/{article_id}",
    description="Update an existing article by its ID."
)
async def update_article(article_id: int):
    pass


@router.post(
    path="/{article_id}/comment",
    description="Add a comment to an article by its ID."
)
async def add_comment(article_id: int):
    pass
