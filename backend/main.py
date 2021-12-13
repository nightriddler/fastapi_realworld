from fastapi import FastAPI

from src.articles.router import router_article
from src.db.database import create_engine_app
from src.users.router import router_user

from settings import config


def create_app():

    app = FastAPI()
    (engine, sessionmaker) = create_engine_app(config.sqlalchemy_db)

    app.state.engine = engine
    app.state.sessionmaker = sessionmaker

    app.include_router(router_user)
    app.include_router(router_article)
    return app


app = create_app()
