from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import decode, encode

from config import PRIVATE_KEY, PUBLIC_KEY
from snowflake import SnowflakeID

from datetime import datetime, timedelta
from typing import Annotated, Union

try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc


SECURITY = HTTPBearer(
    scheme_name="Jwt",
    description="JWT which get from posting discord oauth code to /auth/login.",
    auto_error=False,
)


def sign_jwt(user_id: Union[int, str, SnowflakeID]) -> str:
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(days=7)
    }

    return encode(
        payload=payload,
        key=PRIVATE_KEY,
        algorithm="ES256"
    )


def validate_jwt(token: str) -> dict:
    try:
        return decode(
            token,
            key=PUBLIC_KEY,
            algorithms=["ES256"]
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials."
        )


def validate_depends(token: HTTPAuthorizationCredentials = Security(SECURITY)) -> int:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials."
        )

    jwt = token.credentials
    payload = validate_jwt(jwt)

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials."
        )
    return int(user_id)


UserIdDepends = Depends(validate_depends)
UserIdDep = Annotated[int, UserIdDepends]
