from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from orjson import loads

from asyncio import gather

from auth import UserIdDep, validate_jwt
from conversation_manager import (
    ConversationManager,
    get_conversation_by_id,
    get_conversation_list_by_user_id,
    get_messages_by_conversation_id,
    get_private_conversation,
)
from db import SessionDep
from model.view import ConversationView, MessageView

manager = ConversationManager()

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


@router.get("/")
async def get_conversations(
    user_id: UserIdDep,
    session: SessionDep,
) -> list[ConversationView]:
    return await gather(*[
        ConversationView.from_model(model=c, session=session)
        for c in await get_conversation_list_by_user_id(
            user_id=user_id,
            session=session
        )
    ])


@router.get("/by-id/{conversation_id}")
async def get_by_id(
    user_id: UserIdDep,
    conversation_id: int,
    session: SessionDep,
) -> ConversationView:
    conversation = await get_conversation_by_id(
        user_id=user_id,
        conversation_id=conversation_id,
        session=session,
    )

    return await ConversationView.from_model(
        model=conversation,
        session=session
    )


@router.get("/by-id/{conversation_id}/messages")
async def get_messages(
    user_id: UserIdDep,
    conversation_id: int,
    session: SessionDep,
) -> list[MessageView]:
    messages = await get_messages_by_conversation_id(
        user_id=user_id,
        conversation_id=conversation_id,
        session=session,
    )

    return [
        MessageView.from_model(message)
        for message in messages
    ]


@router.get("/private-message/{to_user_id}")
async def get_private_message(
    user_id: UserIdDep,
    to_user_id: int,
    session: SessionDep,
) -> ConversationView:
    conversation = await get_private_conversation(
        user_id_1=user_id,
        user_id_2=to_user_id,
        session=session,
    )

    return await ConversationView.from_model(
        conversation,
        session=session
    )


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session: SessionDep
):
    await websocket.accept()

    user_id = None
    try:
        token = await websocket.receive_text()
        user_id = validate_jwt(token=token).get("sub", None)
        if user_id is None:
            await websocket.close(code=1008)
            return

        user_id = int(user_id)

        manager.connect(
            ws=websocket,
            user_id=user_id
        )

        while True:
            data = loads(await websocket.receive_text())
            conversation_id = data.get("conversation_id", None)
            message_context = data.get("message", None)
            if conversation_id is None or message_context is None:
                continue

            try:
                conversation_id = int(conversation_id)
            except:
                continue

            await manager.send_message(
                user_id=user_id,
                conversation_id=conversation_id,
                message=message_context,
                session=session
            )
    except WebSocketDisconnect:
        pass
    except:
        from traceback import print_exc
        print_exc()
        await websocket.close(code=1008)
        return
    finally:
        if isinstance(user_id, int):
            await manager.disconnect(
                ws=websocket,
                user_id=user_id,
                conversation_id=None
            )
