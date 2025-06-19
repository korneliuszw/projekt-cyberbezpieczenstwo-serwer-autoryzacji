from datetime import timedelta, datetime, timezone
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import BaseModel

from database import SessionDep
from models import Roles, UserModel
import os

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login",
    scopes={
        "EMPLOYEE": "Can see posts and comment on them",
        "MANAGER": "Can create posts, view them and manage comments",
        "ADMINISTRATOR": "Can do anything with posts, can create and remove users",
    },
)
SECRET_KEY = os.environ.get("PYTHON_SECRET_KEY", "your_secret_key")
ALGORITHM = os.environ.get("PYTHON_ALGORITHM", "HS256")

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
    username: str
    email: str
    scopes: list[Roles] = []
    sid: UUID
    restaurant: str


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
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        restaurant: str = payload.get("restaurant")
        if restaurant is None:
            raise credentials_exception
        scopes: list[Roles] = payload.get("scopes")
        for requested_scope in security_scopes.scopes:
            if requested_scope not in scopes:
                raise HTTPException(
                    status_code=401,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        sid = UUID(payload.get("sid"))
        return TokenData(
            uid=uid, username=username, email=email, sid=sid, scopes=scopes, restaurant=restaurant
        )
    except jwt.PyJWTError:
        raise credentials_exception


async def get_current_user(
    session: SessionDep, token: TokenData = Depends(get_token)
) -> UserModel:
    user_in_db = session.get(UserModel, token.uid)
    if user_in_db is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_in_db


EmployeeRequired = Annotated[UserModel, Security(get_current_user, scopes=["EMPLOYEE"])]
ConsultantRequired = Annotated[
    UserModel, Security(get_current_user, scopes=["MANAGER"])
]
AdministratorRequired = Annotated[
    UserModel, Security(get_current_user, scopes=["ADMIN"])
]
AnyUser = Annotated[UserModel, Depends(get_current_user)]
