from typing import Annotated

from fastapi.params import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

connect_url = f"sqlite:///local.db"
connect_args = {"check_same_thread": False}

engine = create_engine(connect_url, connect_args=connect_args, echo=True)
DbSession = sessionmaker(engine)


def api_get_session():
    with DbSession() as session:
        yield session


SessionDep = Annotated[Session, Depends(api_get_session)]