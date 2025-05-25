import enum
from typing import List

from sqlalchemy import MetaData, Column, ForeignKey, LargeBinary
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.testing.schema import mapped_column


class Roles(enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

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
    email: Mapped[str] = mapped_column()
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary)
    role: Mapped[Roles] = mapped_column()
