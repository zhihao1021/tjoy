from bcrypt import gensalt, hashpw
from fastapi import APIRouter
from jwt import decode, encode

from config import PRIVATE_KEY, PUBLIC_KEY
from db import SessionDep
from model.user import User, UserModel
from schemas.auth import RegisterData
from snowflake import SnowflakeGenerator

router = APIRouter()

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
        username=data.username,
        display_name=data.display_name,
        gender=data.gender,
        password_hash=hashed_password
    )

    user.to_model()
