from pydantic import BaseModel

from models import Roles


class NewUserSchema(BaseModel):
    username: str
    email: str
    password: str
    role: Roles

class GetUserSchema(BaseModel):
    username: str
    email: str
    role: Roles

class DeleteUserSchema(BaseModel):
    username: str
    email: str