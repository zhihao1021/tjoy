from fastapi import APIRouter

router = APIRouter(
    prefix="/friends",
    tags=["Friends"]
)


@router.get(
    path="/",
    description="Get a list of friends for the authenticated user."
)
async def get_friends():
    pass


@router.post(
    path="/add",
    description="Add a new friend by user ID."
)
async def add_friend():
    pass
