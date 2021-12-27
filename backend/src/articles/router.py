from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.params import Depends
from slugify.slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from src.articles import utils
from src.db import models
from src.db.database import get_db
from src.router_setting import APIRouter
from src.users import authorize
from src.users.crud import get_curr_user_by_token, get_user_by_token

from . import crud, schemas

router_article = APIRouter()


@router_article.get(
    "/articles/feed", response_model=schemas.GetArticles, tags=["Articles"]
)
async def get_recent_articles_from_users_you_follow(
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """
    Get most recent articles from users you follow.
    Use query parameters to limit.

    Auth is required
    """
    articles = await crud.feed_article(db, user, limit, offset)
    return schemas.GetArticles(articles=articles, articlesCount=len(articles))


@router_article.get("/articles", response_model=schemas.GetArticles, tags=["Articles"])
async def get_articles(
    request: Request,
    tag: Optional[str] = None,
    author: Optional[str] = None,
    favorited: Optional[str] = None,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Get most recent articles globally.
    Use query parameters to filter results.

    Auth is optional.
    """
    authorization = request.headers.get("Authorization")
    if authorization:
        token = authorize.clear_token(authorization)
        authorization = await get_user_by_token(db, token)
    articles = await crud.get_articles_auth_or_not(
        db, tag, author, favorited, limit, offset, authorization
    )
    return schemas.GetArticles(articles=articles, articlesCount=len(articles))


@router_article.post(
    "/articles",
    response_model=schemas.CreateArticleResponse,
    status_code=201,
    tags=["Articles"],
)
async def set_up_article(
    article_data: schemas.CreateArticleRequest,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """
    Create an article.
    Auth is required.
    """
    slug = slugify(article_data.article.title)
    article = await utils.get_article(db, slug)
    if article:
        raise HTTPException(
            status_code=400, detail="An article with this title already exists."
        )
    article = await crud.create_article(db, article_data, user)
    return schemas.CreateArticleResponse(article=article)


@router_article.get(
    "/articles/{slug}", response_model=schemas.GetArticle, tags=["Articles"]
)
async def get_article(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    """
    Get an article.
    Auth not required.
    """
    article = await utils.get_article(db, slug)

    if not article:
        raise HTTPException(status_code=400, detail="Artcile is not found")
    authorization = request.headers.get("authorization")
    if authorization:
        token = authorize.clear_token(authorization)
        authorization = await get_user_by_token(db, token)
    article = await crud.get_single_article_auth_or_not_auth(db, slug, authorization)
    return schemas.GetArticle(article=article)


@router_article.put(
    "/articles/{slug}", response_model=schemas.GetArticle, tags=["Articles"]
)
async def change_article(
    article_data: schemas.UpdateArticle,
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """
    Update an article.
    Auth is required.
    """
    article = await utils.get_article(db, slug)
    if not article:
        raise HTTPException(status_code=400, detail="Artcile is not found")
    if article.author != user.username:
        raise HTTPException(
            status_code=400, detail="You are not the author of this article"
        )
    await crud.change_article(db, slug, article_data, user)
    article = await crud.get_single_article_auth_or_not_auth(db, slug)
    return schemas.GetArticle(article=article)


@router_article.delete("/articles/{slug}", response_description="OK", tags=["Articles"])
async def remove_article(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """
    Delete an article.
    Auth is required.
    """
    article = await utils.get_article(db, slug)
    if not article:
        raise HTTPException(status_code=400, detail="Artcile is not found")
    if article.author != user.username:
        raise HTTPException(
            status_code=400, detail="You can not delete someone elses article"
        )
    await crud.delete_article(db, slug)
    return Response(status_code=status.HTTP_200_OK)


@router_article.get(
    "/articles/{slug}/comments",
    response_model=schemas.GetCommentsResponse,
    tags=["Comments"],
)
async def select_comment(
    request: Request, slug: str, db: AsyncSession = Depends(get_db)
):
    """
    Get the comments for an article.
    Auth is optional.
    """
    article = await utils.get_article(db, slug)
    if not article:
        raise HTTPException(status_code=400, detail="Article is not found")
    authorization = request.headers.get("authorization")
    if authorization:
        token = authorize.clear_token(authorization)
        authorization = await get_user_by_token(db, token)
    comments = await crud.get_comments(db, slug, authorization)
    return schemas.GetCommentsResponse(comments=comments)


@router_article.post(
    "/articles/{slug}/comments",
    response_model=schemas.GetCommentResponse,
    tags=["Comments"],
)
async def post_comment(
    slug: str,
    comment: schemas.CreateComment,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """
    Create a comment for an article.
    Auth is required.
    """
    article = await utils.get_article(db, slug)
    if not article:
        raise HTTPException(status_code=400, detail="Article is not found")
    comment = await crud.create_comment(db, comment, slug, user)
    return schemas.GetCommentResponse(comment=comment)


@router_article.delete("/articles/{slug}/comments/{id}", tags=["Comments"])
async def remove_comment(
    slug: str,
    id: int,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """
    Delete a comment for an article.
    Auth is required.
    """
    article = await utils.get_article(db, slug)
    if not article:
        raise HTTPException(status_code=400, detail="Article is not found")
    comment = await crud.get_comment(db, slug, id)
    if not comment:
        raise HTTPException(status_code=400, detail="Comment not found")
    if comment.author != user.id:
        raise HTTPException(
            status_code=400, detail="You can only delete your own comment."
        )
    await crud.delete_comment(db, slug, id, user)
    return Response(status_code=status.HTTP_200_OK)


@router_article.post(
    "/articles/{slug}/favorite",
    response_model=schemas.CreateArticleResponse,
    tags=["Favorites"],
)
async def post_favorite(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """
    Favorite an article.
    Auth is required.
    """
    article = await utils.get_article(db, slug)
    if not article:
        raise HTTPException(status_code=400, detail="Article is not found")
    favorite = await utils.check_favorite(db, slug, user.username)
    if favorite:
        raise HTTPException(
            status_code=400,
            detail="You have already added this article to your favorites",
        )
    await crud.create_favorite(db, slug, user)
    article = await crud.get_single_article_auth_or_not_auth(db, slug, user)
    return schemas.CreateArticleResponse(article=article)


@router_article.delete(
    "/articles/{slug}/favorite",
    response_model=schemas.CreateArticleResponse,
    tags=["Favorites"],
)
async def remove_favorite(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_curr_user_by_token),
):
    """
    Unfavorite an article.
    Auth is required.
    """
    article = await utils.get_article(db, slug)
    if not article:
        raise HTTPException(status_code=400, detail="Article is not found")
    favorite = await utils.check_favorite(db, slug, user.username)
    if not favorite:
        raise HTTPException(
            status_code=400, detail="The article was not in my favorites"
        )
    await crud.delete_favorite(db, slug, user)
    article = await crud.get_single_article_auth_or_not_auth(db, slug, user)
    return schemas.CreateArticleResponse(article=article)


@router_article.get("/tags", response_model=schemas.GetTags, tags=["Tags"])
async def get_tags(db: AsyncSession = Depends(get_db)):
    """
    Get tags.
    Auth not required.
    """
    tags = await crud.select_tags(db)
    return schemas.GetTags(tags=tags)
