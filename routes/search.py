from fastapi import APIRouter

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.get(
    path="",
    description="Search"
)
async def search(query: str):
    pass
