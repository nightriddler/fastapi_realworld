from fastapi import FastAPI

from settings import config
from src.articles.router import router_article
from src.db.database import create_engine_async_app
from src.users.router import router_user


def create_app() -> FastAPI:

    app = FastAPI()
    (engine, sessionmaker) = create_engine_async_app(config.sqlalchemy_db)
    app.state.engine = engine
    app.state.sessionmaker = sessionmaker

    app.include_router(router_user)
    app.include_router(router_article)
    return app


app = create_app()
