from bcrypt import checkpw, gensalt, hashpw
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from db import SessionDep
from model.user import User, UserModel
from schemas.auth import Jwt, LoginData, RegisterData
from snowflake import SnowflakeGenerator

from .utils import sign_jwt

router = APIRouter(
    prefix="/auth"
)

id_generator = SnowflakeGenerator()


@router.post("/register")
async def register(session: SessionDep, data: RegisterData):
    salt = gensalt()
    hashed_password = hashpw(
        data.password.encode("utf-8"),
        salt
    )

    user = User(
        id=id_generator.next_id(),
        password_hash=hashed_password,
        **data.model_dump(exclude={"password"})
    )

    session.add(user.to_model())

    try:
        await session.commit()
    except:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed."
        )

    token = sign_jwt(user.id)

    return Jwt(access_token=token)


@router.post("/login")
async def login(session: SessionDep, data: LoginData) -> Jwt:
    result = (await session.execute(select(
        UserModel.id, UserModel.password_hash
    ).where(
        UserModel.username == data.username
    ))).first()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    user_id, password = result

    if not checkpw(data.password.encode("utf-8"), password.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password."
        )
    token = sign_jwt(user_id)

    return Jwt(access_token=token)
