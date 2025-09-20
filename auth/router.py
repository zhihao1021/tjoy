from bcrypt import checkpw, gensalt, hashpw
from fastapi import APIRouter, Body, HTTPException, status
from sqlalchemy import select

from typing import Annotated

from db import SessionDep
from exceptions.user import USER_NOT_FOUND
from model.user import User, UserModel
from schemas.auth import Jwt, LoginData, RegisterData
from snowflake import SnowflakeGenerator

from .utils import sign_jwt, UserIdDep

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

id_generator = SnowflakeGenerator()


@router.post(
    path="/pre-check",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def pre_check(session: SessionDep, username: Annotated[str, Body(embed=True)]) -> None:
    result = (await session.execute(select(
        UserModel.id
    ).where(
        UserModel.username == username
    ))).first()

    if result is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken."
        )


@router.post("/register")
async def register(session: SessionDep, data: RegisterData) -> Jwt:
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
        raise USER_NOT_FOUND

    user_id, password = result

    if not checkpw(data.password.encode("utf-8"), password.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password."
        )
    token = sign_jwt(user_id)

    return Jwt(access_token=token)


@router.put("/refresh")
def refresh_token(user_id: UserIdDep) -> Jwt:
    token = sign_jwt(user_id)

    return Jwt(access_token=token)
