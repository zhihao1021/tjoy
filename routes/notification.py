from fastapi import APIRouter

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get(
    path="",
    description="Get notifications for the authenticated user."
)
async def get_notifications():
    pass
