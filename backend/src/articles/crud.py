from typing import List, Optional

from slugify import slugify
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.articles import schemas
from src.articles.utils import (
    add_favorited,
    add_tags_authors_favorites_time_in_articles,
)
from src.db.models import Article, Comment, Favorite, Follow, Tag, User
from src.users import utils as user_utils
from src.users.crud import check_subscribe


async def get_articles_auth_or_not(
    db: AsyncSession,
    tag: Optional[str] = None,
    author: Optional[str] = None,
    favorited: Optional[str] = None,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    current_user: Optional[User] = None,
) -> List[Article]:
    """
    Get list Article for pydantic model.

    Filtering by tag name, author username, favorited username.
    Optional receipt of articles by limit(default 20), offset(default 0).

    Auth is optional.
    """
    query = select(Article)
    stmt_tag = await db.execute(select(Tag).filter(Tag.name == tag))
    tag_db = stmt_tag.scalars().first()
    if tag:
        if tag_db:
            query = query.join(Article.tag).filter(Article.tag.contains(tag_db))
    if author:
        query = query.where(Article.author == author)
    if favorited:
        query = query.join(Favorite).where(Favorite.user == favorited)
    query = (
        query.order_by(Article.created_at.desc())
        .offset(offset)
        .limit(limit)
        .options(selectinload(Article.tag), selectinload(Article.authors))
    )

    stmt = await db.execute(query)
    articles = stmt.scalars().unique().all()

    articles = await add_tags_authors_favorites_time_in_articles(db, articles)

    if current_user:
        articles = await add_favorited(db, articles, current_user)
        for article in articles:
            article.author = await user_utils.add_following(
                db, article.author, current_user
            )

    return articles


async def feed_article(
    db: AsyncSession, user: User, limit: int, offset: int
) -> List[Article]:
    """
    Gets articles from users you follow.
    Optional receipt of articles by limit(default 20), offset(default 0).

    Auth is required.
    """
    stmt = await db.execute(
        select(Article)
        .join(Follow, Follow.author == Article.author)
        .where(Follow.user == user.username)
        .order_by(Article.created_at.desc())
        .offset(offset)
        .limit(limit)
        .options(selectinload(Article.tag), selectinload(Article.authors))
    )
    articles = stmt.scalars().all()
    articles = await add_tags_authors_favorites_time_in_articles(db, articles)
    articles = await add_favorited(db, articles, user)
    for article in articles:
        article.author = await user_utils.add_following(db, article.author, user)
    return articles


async def create_article(
    db: AsyncSession, data: schemas.CreateArticleRequest, user: User
) -> Article:
    """
    Creating an article based on data from a pydantic query model.
    """
    tags = []
    if data.article.tagList:
        stmt = await db.execute(select(Tag).filter(Tag.name.in_(data.article.tagList)))
        tags_db = stmt.scalars().all()
        await db.close()
        tags = [tag_name for tag_name in tags_db]

    db_article = Article(
        slug=slugify(data.article.title),
        title=data.article.title,
        description=data.article.description,
        body=data.article.body,
        author=user.username,
        tag=tags,
    )
    db.add(db_article)
    await db.commit()
    await db.close()

    db_article.tagList = [tag.name for tag in db_article.tag]
    db_article.author = user
    db_article.createdAt = db_article.created_at
    db_article.updatedAt = db_article.updated_at
    return db_article


async def get_single_article_auth_or_not_auth(
    db: AsyncSession, slug: str, current_user: Optional[User] = None
) -> Article or None:
    """
    Get single Article or None on slug.
    Auth is optional.
    """
    stmt = await db.execute(
        select(Article)
        .where(Article.slug == slug)
        .options(selectinload(Article.tag), selectinload(Article.authors))
    )
    articles = stmt.scalars().all()

    await db.close()
    if not articles:
        return None
    articles = await add_tags_authors_favorites_time_in_articles(db, articles)
    if current_user:
        articles = await add_favorited(db, articles, current_user)
        for article in articles:
            subscribe = await check_subscribe(
                db, current_user.username, article.author.username
            )
            if subscribe:
                article.author.following = True

    return articles[0]


async def change_article(
    db: AsyncSession, slug: str, article_data: schemas.UpdateArticle, user: User
) -> Article:
    """
    Edit Article by slug.
    """
    up_article = (
        update(Article)
        .where(Article.slug == slug)
        .values(author=user.username, **article_data.article.dict(exclude_unset=True))
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(up_article)
    await db.commit()


async def delete_article(db: AsyncSession, slug: str):
    """
    Delete Article by slug.
    """
    del_article = (
        delete(Article)
        .where(Article.slug == slug)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(del_article)
    await db.commit()


async def get_comments(
    db: AsyncSession, slug: str, auth_user: Optional[User] = None
) -> List[Comment]:
    """
    Get article comments on slug.
    Auth is optional.
    """
    stmt = await db.execute(select(Comment).where(Comment.article == slug))
    comments = stmt.scalars().all()
    for comment in comments:
        stmt_author = await db.execute(select(User).where(User.id == comment.author))
        comment.author = stmt_author.scalars().first()
        await db.close()

        if auth_user:
            comment.author = await user_utils.add_following(
                db, comment.author, auth_user
            )
        comment.createdAt = comment.created_at
        comment.updatedAt = comment.updated_at
    return comments


async def create_comment(
    db: AsyncSession, data: schemas.CreateComment, slug: str, user: User
) -> Comment:
    """
    Create a comment for an article by slug and user.
    """
    db_comment = Comment(body=data.comment.body, author=user.id, article=slug)
    db.add(db_comment)
    await db.commit()

    db_comment.author = user
    db_comment.createdAt = db_comment.created_at
    db_comment.updatedAt = db_comment.updated_at
    return db_comment


async def delete_comment(db: AsyncSession, slug: str, id: str, user: User):
    """
    Delete the comment on slug and the author of the article.
    """
    del_comment = (
        delete(Comment)
        .where(Comment.article == slug, Comment.id == id)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(del_comment)
    await db.commit()


async def get_comment(db: AsyncSession, slug: str, id: str) -> Comment:
    """
    Get single comment for an article by slug and id comment.
    """
    stmt = await db.execute(
        select(Comment).where(Comment.article == slug, Comment.id == id)
    )
    comment = stmt.scalars().first()
    return comment


async def create_favorite(db: AsyncSession, slug: str, user: User):
    """
    Create Favorite model by article slug.
    """
    favorite = Favorite(article=slug, user=user.username)
    db.add(favorite)
    await db.commit()


async def delete_favorite(db: AsyncSession, slug: str, user: User):
    """
    Delete Favorite model by article slug and user.
    """
    del_favorite = (
        delete(Favorite)
        .where(Favorite.article == slug, Favorite.user == user.username)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(del_favorite)
    await db.commit()


async def select_tags(db: AsyncSession) -> List[str]:
    """
    Get all tags.
    """
    tags = await db.execute(select(Tag))
    tags_db = tags.scalars().all()
    return [tag.name for tag in tags_db]
