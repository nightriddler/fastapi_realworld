from typing import Optional
from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import Response
from src.users import authorize
from . import schemas, crud
from src.db import models
from src.db.database import get_db
from src.users.crud import get_curr_user_by_token


router_article = APIRouter()


@router_article.get(
    '/articles/',
    response_model=schemas.GetArticles,
    tags=['Articles']
)
def get_articles(
        tag: Optional[str] = None,
        author: Optional[str] = None,
        favorited: Optional[str] = None,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
        db: Session = Depends(get_db)):
    articles = crud.select_articles(db, tag, author, favorited, limit, offset)

    for article in articles:
        article.author = article.authors
        article.tagList = [tag.name for tag in article.tag]
    return schemas.GetArticles(articles=articles, articlesCount=len(articles))


@router_article.post(
    '/articles/',
    response_model=schemas.CreateArticleResponse,
    status_code=201,
    tags=['Articles']
)
def set_up_article(
        article_data: schemas.CreateArticleRequest,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_curr_user_by_token)):
    article = crud.create_article(db, article_data, user)
    article.author = user
    article.tagList = [tag.name for tag in article.tag]
    # article.favorited
    # article.favoritesCount
    return schemas.CreateArticleResponse(article=article)


@router_article.get(
    '/articles/{slug}/',
    response_model=schemas.GetArticle,
    tags=['Articles'])
def get_article(slug: str, db: Session = Depends(get_db)):
    article = crud.get_single_article(db, slug)
    return schemas.GetArticle(article=article)


@router_article.put(
    '/articles/{slug}/',
    response_model=schemas.GetArticle,
    tags=['Articles'])
def change_article(
        article_data: schemas.UpdateArticle,
        slug: str,
        db: Session = Depends(get_db),
        token: str = Depends(authorize.check_token)):
    article = crud.change_article(db, slug, article_data)
    return schemas.GetArticle(article=article)


@router_article.delete(
    '/articles/{slug}/',
    response_description='OK',
    tags=['Articles'])
def remove_article(
        slug: str,
        db: Session = Depends(get_db),
        token: str = Depends(authorize.check_token)):
    crud.delete_article(db, slug)
    return Response(status_code=status.HTTP_200_OK)
