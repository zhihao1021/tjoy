from sqlalchemy import func, insert, select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional

from db import get_session
from exceptions.conversation import CONVERSATION_NOT_FOUND, CREATE_CONVERSATION_ERROR
from model import ConversationModel, MessageModel
from model.relationships import conversation_user_table
from snowflake import SnowflakeGenerator

id_generator = SnowflakeGenerator()


async def get_conversation_by_id(
    conversation_id: int,
    user_id: Optional[int] = None,
    session: Optional[AsyncSession] = None
) -> ConversationModel:
    async with get_session(session) as session:
        stat = select(ConversationModel)

        if user_id:
            stat = stat.join(
                conversation_user_table,
                conversation_user_table.c.conversations_id == ConversationModel.id
            ).where(
                ConversationModel.id == conversation_id,
                conversation_user_table.c.user_id == user_id
            )
        else:
            stat = stat.where(
                ConversationModel.id == conversation_id
            )

        result = await session.execute(stat.options(
            joinedload(ConversationModel.users),
            joinedload(ConversationModel.event),
        ))

        conversation = result.scalars().first()

        if conversation is None:
            raise CONVERSATION_NOT_FOUND

        return conversation


async def get_conversation_list_by_user_id(
    user_id: int,
    session: Optional[AsyncSession] = None
) -> list[ConversationModel]:
    async with get_session(session) as session:
        conversations = await session.execute(select(
            ConversationModel,
        ).join(
            conversation_user_table,
            conversation_user_table.c.conversations_id == ConversationModel.id
        ).options(
            joinedload(ConversationModel.users),
            joinedload(ConversationModel.event),
        ).where(
            conversation_user_table.c.user_id == user_id
        ))

        return list(conversations.scalars().unique().all())


async def get_private_conversation(
    user_id_1: int,
    user_id_2: int,
    session: Optional[AsyncSession] = None
) -> ConversationModel:
    async with get_session(session) as session:
        result = await session.execute(select(
            ConversationModel
        ).join(
            conversation_user_table,
            conversation_user_table.c.conversations_id == ConversationModel.id
        ).where(
            ConversationModel.is_private == True,
            conversation_user_table.c.user_id.in_([user_id_1, user_id_2])
        ).options(
            joinedload(ConversationModel.users),
            joinedload(ConversationModel.event),
        ).group_by(ConversationModel.id).having(
            func.count(ConversationModel.id) == 2
        ))

        conversation = result.scalars().first()

        if conversation is not None:
            return conversation

        conversation = ConversationModel(
            id=id_generator.next_id(),
            title="",
            is_private=True
        )

        session.add(conversation)
        await session.execute(insert(
            conversation_user_table
        ).values([
            {"user_id": user_id_1, "conversations_id": conversation.id},
            {"user_id": user_id_2, "conversations_id": conversation.id}
        ]))

        try:
            await session.commit()
        except:
            await session.rollback()
            raise CREATE_CONVERSATION_ERROR

        await session.refresh(conversation)

        return conversation


async def get_messages_by_conversation_id(
    user_id: int,
    conversation_id: int,
    session: Optional[AsyncSession] = None
) -> list[MessageModel]:
    async with get_session(session) as session:
        messages = await session.execute(select(
            MessageModel
        ).where(
            MessageModel.author_id == user_id,
            MessageModel.conversation_id == conversation_id,
        ).order_by(
            MessageModel.id.asc()
        ))

        return list(messages.scalars().all())
