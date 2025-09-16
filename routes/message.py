from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websocket.connec_manager import ConnectionManager

manager = ConnectionManager()

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

