import enum
from typing import List

from sqlalchemy import MetaData, Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.testing.schema import mapped_column


class Roles(enum.Enum):
    EMPLOYEE = 1
    MANAGER = 2
    ADMIN = 3

class Base(DeclarativeBase):
    uppercase_naming_convention = {
        "ix": "IX_%(table_name)s_%(column_0_N_name)s",  # Indexes
        "uq": "UQ_%(table_name)s_%(column_0_N_name)s",  # Unique constraints
        "ck": "CK_%(table_name)s_%(constraint_name)s",  # Check constraints
        "fk": "FK_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",  # Foreign keys
        "pk": "PK_%(table_name)s",  # Primary keys
    }
    metadata = MetaData(naming_convention=uppercase_naming_convention)

class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column()
    role: Mapped[Roles] = mapped_column()

class PostModel(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    tag: Mapped[str] = mapped_column()
    comments: Mapped[List["CommentModel"]] = relationship(back_populates="post")

class CommentModel(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column()
    author_id: Mapped[int] = mapped_column(ForeignKey(UserModel.id))
    post_id: Mapped[int] = mapped_column(ForeignKey(PostModel.id))
    author: Mapped[UserModel] = relationship(remote_side=UserModel.id)
    post: Mapped[PostModel] = relationship(back_populates="comments")
