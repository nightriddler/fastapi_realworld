from typing import Tuple
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from starlette.requests import Request


def create_engine_app(db_url) -> Tuple[Engine, sessionmaker]:
    engine = create_engine(db_url)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, session


def get_db(request: Request) -> Session:
    db = request.app.state.sessionmaker()
    with db as database:
        yield database
        database.close()
