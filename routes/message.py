from fastapi import APIRouter

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


@router.get("/")
async def get_messages():
    pass


@router.get("/{message_id}")
async def get_message(message_id: int):
    pass


@router.websocket("/ws/{message_id}")
async def websocket_endpoint(message_id: int):
    pass
