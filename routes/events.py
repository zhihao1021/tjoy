from fastapi import APIRouter

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


@router.post(
    path="/{event_id}",
    description="Join an event by its ID."
)
async def join_event(event_id: int):
    pass
