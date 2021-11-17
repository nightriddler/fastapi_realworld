from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session
from src.db.models import Article, Favorite, User


def check_favorite(db: Session, slug: str, username: str) -> bool:
    check = db.query(Favorite).filter(
        Favorite.user == username, Favorite.article == slug
    )
    return db.query(check.exists()).scalar()


def add_favorited(
    db: Session, articles: List[Article], current_user: User
) -> List[Article]:
    """Change field "favorited" in Article pydantic model for articles.
    If there is authorizatrion."""
    favorites_user = (
        db.query(Favorite).where(Favorite.user == current_user.username).all()
    )
    favorites_user_article = {
        favorite.article: favorite.user for favorite in favorites_user
    }
    # >>> {'444': 'first', '777': 'first', '555': 'first', '999': 'first'}

    # Второй вариант. Мне кажется он менее оптимальный.
    # articles_favorites = db.query(Favorite).all()
    # favorites = [article.article for article in articles_favorites]
    # count_favorite_articles = Counter(favorites)
    for article in articles:
        if article.slug in favorites_user_article:
            article.favorited = True
    return articles


def add_tags_authors_favorites_time_in_articles(
    db: Session, articles: List[Article]
) -> List[Article]:
    """Add tags, authors, created and updated time
    in articles for Article pydantic model."""
    favorites = (
        db.query(Favorite.article, func.count(Favorite.article))
        .group_by(Favorite.article)
        .all()
    )
    # >>> [('444', 2), ('222', 1), ('777', 1)]
    count_favorite_articles = {article[0]: article[1] for article in favorites}
    # >>> {'444': 2, '222': 1, '777': 1}
    for article in articles:
        article.author = article.authors
        article.tagList = [tag.name for tag in article.tag]
        if article.slug in count_favorite_articles:
            article.favoritesCount = count_favorite_articles[article.slug]
        article.createdAt = article.created_at
        article.updatedAt = article.updated_at
    return articles
