from fastapi import FastAPI

from src.articles.router import router_article
from src.db import models
from src.db.database import engine
from src.users.router import router_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(router_user)
app.include_router(router_article)
