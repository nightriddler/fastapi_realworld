from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request


def create_engine_app(db_url):
    engine = create_engine(db_url)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, session


def get_db(request: Request):
    db = request.app.state.sessionmaker()
    with db as database:
        yield database
        database.close()
