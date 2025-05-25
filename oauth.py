from datetime import timedelta, datetime, timezone
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import BaseModel

from database import SessionDep
from models import UserRole, UserModel
from repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login",
    scopes={
        "ADMIN": "Can manage users",
        "CONSULTANT": "Can create invoices and view tariffs",
        "SERVICEMAN": "Can create and edit downtime logs",
    },
)
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

credentials_exception = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    uid: int
    scopes: list[UserRole] = []
    sid: UUID


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_token(
        security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: int = payload.get("uid")
        if uid is None:
            raise credentials_exception
        scopes: list[UserRole] = payload.get("scopes")
        for requested_scope in security_scopes.scopes:
            if requested_scope not in scopes:
                raise HTTPException(
                    status_code=401,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        sid = UUID(payload.get("sid"))
        return TokenData(uid=uid, sid=sid, scopes=scopes)
    except jwt.PyJWTError:
        raise credentials_exception


async def get_current_user(
        session: SessionDep, token: TokenData = Depends(get_token)
) -> UserModel:
    user_in_db = UserRepository.get_by_id(session, token.uid)
    if user_in_db is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif user_in_db.current_session_id != token.sid:
        raise HTTPException(
            status_code=401,
            detail="Session expired",
        )
    return user_in_db


AdminRequired = Annotated[UserModel, Security(get_current_user, scopes=["ADMIN"])]
ConsultantRequired = Annotated[
    UserModel, Security(get_current_user, scopes=["CONSULTANT"])
]
ServicemanRequired = Annotated[
    UserModel, Security(get_current_user, scopes=["SERVICEMAN"])
]
AnyUser = Annotated[UserModel, Depends(get_current_user)]