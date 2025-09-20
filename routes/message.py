from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from auth import UserIdDep
from db import SessionDep
from conversation_manager import (
    ConversationManager,
    get_private_conversation,
)

manager = ConversationManager()

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


@router.get("/")
async def get_messages():
    pass


@router.get("/private-message/{to_user_id}")
async def get_private_message(
    user_id: UserIdDep,
    to_user_id: int,
    session: SessionDep,
):
    conversation = await get_private_conversation(
        user_id_1=user_id,
        user_id_2=to_user_id,
        session=session,
    )


@router.websocket("/ws/{message_id}")
async def websocket_endpoint(websocket: WebSocket, message_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
