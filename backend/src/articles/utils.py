from typing import List

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.models import Article, Favorite, User


async def check_favorite(db: AsyncSession, slug: str, username: str) -> bool:
    """
    Checking an article in the user's favorites.
    """
    stmt = await db.execute(
        select(Favorite).filter(Favorite.user == username, Favorite.article == slug)
    )
    favorite = stmt.scalars().first()
    return True if favorite else False


async def add_favorited(
    db: AsyncSession, articles: List[Article], current_user: User
) -> List[Article]:
    """
    Change field "favorited" in Article pydantic model for articles.
    If there is authorizatrion.
    """
    stmt = await db.execute(
        select(Favorite).where(Favorite.user == current_user.username)
    )
    favorites_user = stmt.scalars().all()
    await db.close()
    favorites_user_article = {
        favorite.article: favorite.user for favorite in favorites_user
    }
    for article in articles:
        if article.slug in favorites_user_article:
            article.favorited = True
    return articles


async def add_tags_authors_favorites_time_in_articles(
    db: AsyncSession, articles: List[Article]
) -> List[Article]:
    """
    Add tags, authors, created and updated time
    in articles for Article pydantic model.
    """
    stmt = await db.execute(
        select(Favorite.article, func.count(Favorite.article)).group_by(
            Favorite.article
        )
    )
    favorites = stmt.all()
    await db.close()
    count_favorite_articles = {article[0]: article[1] for article in favorites}
    for article in articles:
        if not isinstance(article.author, User):
            article.author = article.authors
        article.tagList = [tag.name for tag in article.tag]
        if article.slug in count_favorite_articles:
            article.favoritesCount = count_favorite_articles[article.slug]
        article.createdAt = article.created_at
        article.updatedAt = article.updated_at
    return articles


async def get_article(db: AsyncSession, slug: str) -> bool:
    """
    Get the article by slug.
    """
    stmt = await db.execute(select(Article).filter(Article.slug == slug))
    article = stmt.scalars().first()
    await db.close()
    return article
