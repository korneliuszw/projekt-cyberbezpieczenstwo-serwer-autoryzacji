import uuid
from datetime import timedelta
from typing import Annotated, List

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import SessionDep
from models import UserModel, Roles
from oauth import create_access_token, Token, AdministratorRequired
from schema import NewUserSchema, GetUserSchema, DeleteUserSchema

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@users_router.post("/login")
async def login(
    data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
):
    db_user = (
        session.query(UserModel).filter(UserModel.username == data.username).first()
    )
    if not db_user or not bcrypt.checkpw(
        data.password.encode("utf-8"), db_user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Invalid login or password")
    session_id = uuid.uuid4()
    if db_user.role == Roles.ADMIN:
        scopes = [Roles.ADMIN.value, Roles.MANAGER.value, Roles.EMPLOYEE.value]
    else:
        scopes = [db_user.role.value]
    access_token = create_access_token(
        data={
            "scopes": scopes,
            "uid": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "sid": str(session_id),
        },
        expires_delta=timedelta(hours=1),
    )
    return Token(access_token=access_token, token_type="bearer")


@users_router.get("/", response_model=List[GetUserSchema])
async def get_users(_: AdministratorRequired, session: SessionDep):
    users = session.query(UserModel).all()
    return users


@users_router.post("/", status_code=201)
async def create_user(
    _: AdministratorRequired, new_user: NewUserSchema, session: SessionDep
):
    existing_user_by_username = (
        session.query(UserModel).filter(UserModel.username == new_user.username).first()
    )
    if existing_user_by_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_user_by_email = (
        session.query(UserModel).filter(UserModel.email == new_user.email).first()
    )
    if existing_user_by_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    model = UserModel(
        username=new_user.username,
        email=new_user.email,
        hashed_password=bcrypt.hashpw(
            new_user.password.encode("utf-8"), bcrypt.gensalt()
        ),
        role=new_user.role.value,
    )
    session.add(model)
    session.commit()


@users_router.delete("/", status_code=204)
async def delete_user(
    delete_data: DeleteUserSchema,
    current_user: AdministratorRequired,
    session: SessionDep,
):
    user_to_delete = (
        session.query(UserModel)
        .filter(
            UserModel.username == delete_data.username,
            UserModel.email == delete_data.email,
        )
        .first()
    )
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    if delete_data.username == "admin" and delete_data.email == "admin@admin.com":
        raise HTTPException(status_code=403, detail="Cannot delete the main admin user")

    if current_user.username == delete_data.username:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    session.delete(user_to_delete)
    session.commit()

    return {"message": "User deleted successfully"}
