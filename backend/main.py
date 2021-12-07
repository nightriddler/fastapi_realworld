from fastapi import FastAPI

from src.articles.router import router_article
from src.users.router import router_user


app = FastAPI()


app.include_router(router_user)
app.include_router(router_article)
