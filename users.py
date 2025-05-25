import uuid
from datetime import timedelta
from sqlite3 import IntegrityError
from typing import Annotated, List

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import SessionDep
from models import UserModel, Roles
from oauth import create_access_token, Token, AdministratorRequired
from schema import NewUserSchema, GetUserSchema

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@users_router.post("/login")
async def login(
        data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
):
    db_user = session.query(UserModel).filter(UserModel.username == data.username).first()
    if not db_user or not bcrypt.checkpw(data.password.encode("utf-8"), db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid login or password")
    session_id = uuid.uuid4()
    if db_user.role == Roles.ADMIN:
        scopes = [
            Roles.ADMIN.value,
            Roles.MANAGER.value,
            Roles.EMPLOYEE.value
        ]
    else:
        scopes = [db_user.role.value]
    access_token = create_access_token(data={"scopes": scopes, "uid": db_user.id, "sid": str(session_id)}, expires_delta=timedelta(hours=1))
    return Token(access_token=access_token, token_type="bearer")

@users_router.get("/", response_model=List[GetUserSchema])
async def get_users(_: AdministratorRequired, session: SessionDep):
    users = session.query(UserModel).all()
    return users

@users_router.post("/", status_code=201)
async def create_user(_: AdministratorRequired, new_user: NewUserSchema, session: SessionDep):
    model = UserModel(
        username=new_user.username,
        email=new_user.email,
        hashed_password=bcrypt.hashpw(new_user.password.encode("utf-8"), bcrypt.gensalt()),
        role=new_user.role.value,
    )
    try:
        session.add(model)
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")

