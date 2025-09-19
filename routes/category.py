from fastapi import APIRouter, Body, HTTPException, status

from typing import Annotated

from db import SessionDep
from model import Category
from model.view import CategoryView
from services.category import get_all_categories
from snowflake import SnowflakeGenerator

id_generator = SnowflakeGenerator()

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get(
    path="",
    description="Get list of categories.",
    status_code=status.HTTP_200_OK
)
async def list_categories() -> list[CategoryView]:
    return await get_all_categories()


@router.post(
    path="",
    description="Create a new category.",
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    name: Annotated[str, Body(embed=True)],
    session: SessionDep,
) -> CategoryView:
    category = Category(
        id=id_generator.next_id(),
        name=name,
    )

    session.add(category.to_model())

    try:
        await session.commit()
    except:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create category."
        )

    return CategoryView(
        id=category.id,
        name=category.name
    )
