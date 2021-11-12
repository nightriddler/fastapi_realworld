from typing import Optional
from fastapi import APIRouter, status
# from fastapi import Header
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import Response
from src.users.crud import get_curr_user_by_token
from src.users import authorize
from . import schemas, crud
from src.db import models
from src.db.database import get_db


router_article = APIRouter()


@router_article.get(
    '/articles/feed',
    response_model=schemas.GetArticles,
    tags=['Articles'])
def get_recent_articles_from_users_you_follow(
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_curr_user_by_token)):
    articles = crud.feed_article(db, user, limit, offset)
    return schemas.GetArticles(articles=articles, articlesCount=len(articles))


@router_article.get(
    '/articles',
    response_model=schemas.GetArticles,
    tags=['Articles'])
def get_articles(
        tag: Optional[str] = None,
        author: Optional[str] = None,
        favorited: Optional[str] = None,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
        db: Session = Depends(get_db),
        # Вариант не работает, потому что в Swagger'e
        # появляется поле для ввода authorization.
        # Либо оставлять, игнорируя Swagger (в постмане
        # то все работает), либо искать варианты.
        # authorization: Optional[str] = Header(None),
        ):
    # if authorization:
    #     token = authorize.clear_token(authorization)
    #     user = get_curr_user_by_token(db, token)
    articles = crud.select_articles(db, tag, author, favorited, limit, offset)
    return schemas.GetArticles(articles=articles, articlesCount=len(articles))


@router_article.post(
    '/articles',
    response_model=schemas.CreateArticleResponse,
    status_code=201,
    tags=['Articles'])
def set_up_article(
        article_data: schemas.CreateArticleRequest,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_curr_user_by_token)):
    article = crud.create_article(db, article_data, user)
    return schemas.CreateArticleResponse(article=article)


@router_article.get(
    '/articles/{slug}',
    response_model=schemas.GetArticle,
    tags=['Articles'])
def get_article(slug: str, db: Session = Depends(get_db)):
    article = crud.get_single_article(db, slug)
    return schemas.GetArticle(article=article)


@router_article.put(
    '/articles/{slug}',
    response_model=schemas.GetArticle,
    tags=['Articles'])
def change_article(
        article_data: schemas.UpdateArticle,
        slug: str,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_curr_user_by_token)):
    article = crud.change_article(db, slug, article_data, user)
    return schemas.GetArticle(article=article)


@router_article.delete(
    '/articles/{slug}',
    response_description='OK',
    tags=['Articles'])
def remove_article(
        slug: str,
        db: Session = Depends(get_db),
        token: str = Depends(authorize.check_token)):
    crud.delete_article(db, slug)
    return Response(status_code=status.HTTP_200_OK)


@router_article.get(
    '/articles/{slug}/comments',
    response_model=schemas.GetCommentsResponse,
    tags=['Comments'])
def select_comment(
        slug: str,
        db: Session = Depends(get_db)):
    comments = crud.get_comments(db, slug)
    return schemas.GetCommentsResponse(comments=comments)


@router_article.post(
    '/articles/{slug}/comments',
    response_model=schemas.GetCommentResponse,
    tags=['Comments'])
def post_comment(
        slug: str,
        comment: schemas.CreateComment,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_curr_user_by_token)):
    comment = crud.create_comment(db, comment, slug, user)
    # comment.article = slug
    comment.author = user
    return schemas.GetCommentResponse(comment=comment)


@router_article.delete(
    '/articles/{slug}/comments/{id}',
    tags=['Comments'])
def remove_comment(
        slug: str,
        id: int,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_curr_user_by_token)):
    crud.delete_comment(db, slug, id, user)
    return Response(status_code=status.HTTP_200_OK)


@router_article.post(
    '/articles/{slug}/favorite',
    response_model=schemas.CreateArticleResponse,
    tags=['Favorites'])
def post_favorite(
        slug: str,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_curr_user_by_token)):
    article = crud.create_favorite(db, slug, user)
    return schemas.CreateArticleResponse(article=article)


@router_article.delete(
    '/articles/{slug}/favorite',
    response_model=schemas.CreateArticleResponse,
    tags=['Favorites'])
def remove_favorite(
        slug: str,
        db: Session = Depends(get_db),
        user: models.User = Depends(get_curr_user_by_token)):
    crud.delete_favorite(db, slug, user)
    article = crud.get_single_article(db, slug)
    return schemas.CreateArticleResponse(article=article)


@router_article.get(
    '/tags',
    response_model=schemas.GetTags,
    tags=['default'])
def get_tags(db: Session = Depends(get_db)):
    tags = crud.select_tags(db)
    return schemas.GetTags(tags=tags)
