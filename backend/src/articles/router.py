from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.params import Depends
from slugify.slugify import slugify
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.articles import utils
from src.db import models
from src.db.database import get_db
from src.users import authorize
from src.users.crud import get_curr_user_by_token

from . import crud, schemas

router_article = APIRouter()


@router_article.get(
    "/articles/feed", response_model=schemas.GetArticles, tags=["Articles"]
)
def get_recent_articles_from_users_you_follow(
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """Get most recent articles from users you follow.
    Use query parameters to limit. Auth is required"""
    articles = crud.feed_article(db, user, limit, offset)
    return schemas.GetArticles(articles=articles, articlesCount=len(articles))


@router_article.get("/articles", response_model=schemas.GetArticles, tags=["Articles"])
def get_articles(
    request: Request,
    tag: Optional[str] = None,
    author: Optional[str] = None,
    favorited: Optional[str] = None,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    db: Session = Depends(get_db),
):
    """Get most recent articles globally.
    Use query parameters to filter results. Auth is optional."""
    authorization = request.headers.get("Authorization")
    if authorization:
        token = authorize.clear_token(authorization)
        auth_user = get_curr_user_by_token(db, token)
        articles = crud.get_articles_auth_or_not(
            db, tag, author, favorited, limit, offset, auth_user
        )
    else:
        articles = crud.get_articles_auth_or_not(
            db, tag, author, favorited, limit, offset
        )
    return schemas.GetArticles(articles=articles, articlesCount=len(articles))


@router_article.post(
    "/articles",
    response_model=schemas.CreateArticleResponse,
    status_code=201,
    tags=["Articles"],
)
def set_up_article(
    article_data: schemas.CreateArticleRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """Create an article. Auth is required."""
    slug = slugify(article_data.article.title)
    article = crud.get_single_article_auth_or_not_auth(db, slug)
    if article:
        raise HTTPException(
            status_code=400, detail="An article with this title already exists."
        )
    article = crud.create_article(db, article_data, user)
    return schemas.CreateArticleResponse(article=article)


@router_article.get(
    "/articles/{slug}", response_model=schemas.GetArticle, tags=["Articles"]
)
def get_article(request: Request, slug: str, db: Session = Depends(get_db)):
    """Get an article. Auth not required."""
    authorization = request.headers.get("authorization")
    if authorization:
        token = authorize.clear_token(authorization)
        auth_user = get_curr_user_by_token(db, token)
        article = crud.get_single_article_auth_or_not_auth(db, slug, auth_user)
    else:
        article = crud.get_single_article_auth_or_not_auth(db, slug)
    if not article:
        raise HTTPException(status_code=400, detail="Artcile is not found")
    return schemas.GetArticle(article=article)


@router_article.put(
    "/articles/{slug}", response_model=schemas.GetArticle, tags=["Articles"]
)
def change_article(
    article_data: schemas.UpdateArticle,
    slug: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """Update an article. Auth is required."""
    check = crud.get_single_article_auth_or_not_auth(db, slug)
    if not check:
        raise HTTPException(status_code=400, detail="Artcile is not found")
    if check.author.username != user.username:
        raise HTTPException(
            status_code=400, detail="You are not the author of this article"
        )
    article = crud.change_article(db, slug, article_data, user)
    return schemas.GetArticle(article=article)


@router_article.delete("/articles/{slug}", response_description="OK", tags=["Articles"])
def remove_article(
    slug: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """Delete an article. Auth is required."""
    article = crud.get_single_article_auth_or_not_auth(db, slug)
    if not article:
        raise HTTPException(status_code=400, detail="Artcile is not found")
    if article.author.username != user.username:
        raise HTTPException(
            status_code=400, detail="You can not delete someone elses article"
        )
    crud.delete_article(db, slug)
    return Response(status_code=status.HTTP_200_OK)


@router_article.get(
    "/articles/{slug}/comments",
    response_model=schemas.GetCommentsResponse,
    tags=["Comments"],
)
def select_comment(request: Request, slug: str, db: Session = Depends(get_db)):
    """Get the comments for an article. Auth is optional."""
    article = crud.get_single_article_auth_or_not_auth(db, slug)
    if not article:
        raise HTTPException(status_code=400, detail="Article is not found")
    authorization = request.headers.get("authorization")
    if authorization:
        token = authorize.clear_token(authorization)
        auth_user = get_curr_user_by_token(db, token)
        comments = crud.get_comments(db, slug, auth_user)
    else:
        comments = crud.get_comments(db, slug)
    return schemas.GetCommentsResponse(comments=comments)


@router_article.post(
    "/articles/{slug}/comments",
    response_model=schemas.GetCommentResponse,
    tags=["Comments"],
)
def post_comment(
    slug: str,
    comment: schemas.CreateComment,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """Create a comment for an article. Auth is required."""
    article = crud.get_single_article_auth_or_not_auth(db, slug, user)
    if not article:
        raise HTTPException(status_code=400, detail="Article is not found")
    comment = crud.create_comment(db, comment, slug, user)
    return schemas.GetCommentResponse(comment=comment)


@router_article.delete("/articles/{slug}/comments/{id}", tags=["Comments"])
def remove_comment(
    slug: str,
    id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """Delete a comment for an article. Auth is required."""
    article = crud.get_single_article_auth_or_not_auth(db, slug)
    if not article:
        raise HTTPException(status_code=400, detail="Article is not found")
    if article.author != user:
        raise HTTPException(
            status_code=400, detail="You can only delete your own article."
        )
    comment = crud.get_comment(db, slug, id)
    if not comment:
        raise HTTPException(status_code=400, detail="Comment not found")
    crud.delete_comment(db, slug, id, user)
    return Response(status_code=status.HTTP_200_OK)


@router_article.post(
    "/articles/{slug}/favorite",
    response_model=schemas.CreateArticleResponse,
    tags=["Favorites"],
)
def post_favorite(
    slug: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """Favorite an article. Auth is required."""
    article_check = crud.get_single_article_auth_or_not_auth(db, slug)
    if not article_check:
        raise HTTPException(status_code=400, detail="Article is not found")
    favorite = utils.check_favorite(db, slug, user.username)
    if favorite:
        raise HTTPException(
            status_code=400,
            detail="You have already added this article to your favorites",
        )
    crud.create_favorite(db, slug, user)
    article = crud.get_single_article_auth_or_not_auth(db, slug, user)
    return schemas.CreateArticleResponse(article=article)


@router_article.delete(
    "/articles/{slug}/favorite",
    response_model=schemas.CreateArticleResponse,
    tags=["Favorites"],
)
def remove_favorite(
    slug: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """Unfavorite an article. Auth is required."""
    article_check = crud.get_single_article_auth_or_not_auth(db, slug)
    if not article_check:
        raise HTTPException(status_code=400, detail="Article is not found")
    favorite = utils.check_favorite(db, slug, user.username)
    if not favorite:
        raise HTTPException(
            status_code=400, detail="The article was not in my favorites"
        )
    crud.delete_favorite(db, slug, user)
    article = crud.get_single_article_auth_or_not_auth(db, slug, user)
    return schemas.CreateArticleResponse(article=article)


@router_article.get("/tags", response_model=schemas.GetTags, tags=["default"])
def get_tags(db: Session = Depends(get_db)):
    """Get tags. Auth not required."""
    tags = crud.select_tags(db)
    return schemas.GetTags(tags=tags)
