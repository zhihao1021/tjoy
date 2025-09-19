from asyncio import run
from sqlalchemy import insert, select
from db import Base, engine, get_session
from model.user import UserModel
from dotenv import load_dotenv
load_dotenv(".env")


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with get_session() as session:
        result = await session.execute(select(
            UserModel.id, UserModel.username
        ).where(
            UserModel.username == "testuser"
        ))

        print(result.first())
        # user = UserModel(
        #     id=123,
        #     username="testuser",
        #     display_name="Test User",
        #     gender="Other",
        #     department="Testing",
        #     password_hash="hashedpassword"
        # )

        # session.add(user)

        # try:
        #     await session.commit()
        # except:
        #     await session.rollback()
        #     raise

        # # await session.commit()

        # # result = await session.execute(select(
        # #     UserModel.id
        # # ).)
        # # user = result.first()

        # print(user)


if __name__ == "__main__":
    run(main())
