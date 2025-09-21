from fastapi import WebSocket
from orjson import dumps
from starlette.websockets import WebSocketState
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from asyncio import gather
from typing import Optional

from db import get_session
from model import ConversationModel, MessageModel, UserModel
from model.view import MessageView
from snowflake import SnowflakeGenerator
from translate import translate_text

id_generator = SnowflakeGenerator()


class ConversationManager:
    user_ws: dict[int, list[WebSocket]]
    conversations: dict[int, list[int]]

    def __init__(self) -> None:
        self.user_ws = {}
        self.conversations = {}

    def connect(
        self,
        ws: WebSocket,
        user_id: int
    ) -> None:
        if self.user_ws.get(user_id) is None:
            self.user_ws[user_id] = []

        self.user_ws[user_id].append(ws)

    async def send_message(
        self,
        user_id: int,
        conversation_id: int,
        message: str,
        session: Optional[AsyncSession] = None
    ) -> None:
        async with get_session(session) as session:
            conversation_user_ids = self.conversations.get(conversation_id)
            if conversation_user_ids is None:
                results = await session.execute(select(
                    UserModel.id
                ).join(
                    ConversationModel.users
                ).where(
                    ConversationModel.id == conversation_id
                ))

                conversation_user_ids = list(
                    results.scalars().unique().all()
                )
                self.conversations[conversation_id] = conversation_user_ids
            elif user_id not in conversation_user_ids:
                return

            message_data = MessageModel(
                id=id_generator.next_id().value,
                author_id=user_id,
                conversation_id=conversation_id,
                context=message,
                translated_context=await translate_text(message),
            )

            session.add(message_data)
            try:
                await session.commit()
                await session.refresh(message_data)
            except:
                await session.rollback()
                return

            async def func(user_id: int) -> None:
                async def __func(ws: WebSocket) -> None:
                    if ws.client_state != WebSocketState.CONNECTED:
                        await self.disconnect(
                            ws=ws,
                            user_id=user_id,
                            conversation_id=conversation_id
                        )
                        return

                    await ws.send_bytes(dumps(
                        MessageView.from_model(message_data).model_dump()
                    ))

                await gather(*[__func(ws) for ws in self.user_ws[user_id]])

            await gather(*[
                func(user_id)
                for user_id in conversation_user_ids
                if self.user_ws.get(user_id) is not None
            ])

    async def disconnect(
        self,
        ws: WebSocket,
        user_id: int,
        conversation_id: Optional[int] = None
    ) -> None:
        if self.user_ws.get(user_id) is None:
            return

        self.user_ws[user_id].remove(ws)
        if len(self.user_ws[user_id]) == 0:
            del self.user_ws[user_id]

        if conversation_id is not None:
            need_clean = True
            for user_id in self.conversations.get(conversation_id, []):
                if self.user_ws.get(user_id) is None:
                    continue

                need_clean = False
                break
            if need_clean:
                del self.conversations[conversation_id]

        try:
            await ws.close()
        except:
            pass
