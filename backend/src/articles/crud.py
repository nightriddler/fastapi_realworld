from typing import List, Optional

from slugify import slugify
from sqlalchemy import delete, update
from sqlalchemy.orm import Session, contains_eager
from sqlalchemy.sql.expression import or_

from src.articles import schemas
from src.articles.utils import (
    add_favorited,
    add_tags_authors_favorites_time_in_articles,
)
from src.db.models import Article, Comment, Favorite, Follow, Tag, User
from src.users import utils as user_utils
from src.users.crud import check_subscribe


def get_articles_auth_or_not(
    db: Session,
    tag: Optional[str] = None,
    author: Optional[str] = None,
    favorited: Optional[str] = None,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    current_user: Optional[User] = None,
) -> List[Article]:
    """Get list Article for pydantic model. Auth is optional.
    Filtering by tag name, author username, favorited username.
    Optional receipt of articles by limit(default 20), offset(default 0).
    Auth is optional."""
    query = db.query(Article)
    if tag:
        tag_from_db = db.query(Tag).filter(Tag.name == tag).first()
        if tag_from_db:
            query = query.join(Article.tag).filter(Article.tag.contains(tag_from_db))
        else:
            return []
    if author:
        query = query.filter(or_(author is None, Article.author == author))
    if favorited:
        query = query.join(Favorite).where(Favorite.user == favorited)
    articles = (
        query.order_by(Article.created_at.desc()).offset(offset).limit(limit).all()
    )
    articles = add_tags_authors_favorites_time_in_articles(db, articles)

    if current_user:
        articles = add_favorited(db, articles, current_user)
        for article in articles:
            article.author = user_utils.add_following(db, article.author, current_user)
    return articles


def feed_article(db: Session, user: User, limit: int, offset: int) -> List[Article]:
    """Gets articles from users you follow.
    Optional receipt of articles by limit(default 20), offset(default 0)."""
    articles = (
        db.query(Article)
        .join(Follow, Follow.author == Article.author)
        .where(Follow.user == user.username)
        .order_by(Article.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    articles = add_tags_authors_favorites_time_in_articles(db, articles)
    articles = add_favorited(db, articles, user)
    for article in articles:
        article.author = user_utils.add_following(db, article.author, user)
    return articles


def create_article(
    db: Session, data: schemas.CreateArticleRequest, user: User
) -> Article:
    """Creating an article based on data from a pydantic query model."""
    tags = []
    if data.article.tagList:
        tags = [
            tag_name
            for tag_name in db.query(Tag)
            .filter(Tag.name.in_(data.article.tagList))
            .all()
        ]

    db_article = Article(
        slug=slugify(data.article.title),
        title=data.article.title,
        description=data.article.description,
        body=data.article.body,
        author=user.username,
        tag=tags,
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)

    db_article.tagList = [tag.name for tag in db_article.tag]
    db_article.author = user
    db_article.createdAt = db_article.created_at
    db_article.updatedAt = db_article.updated_at
    return db_article


def get_single_article_auth_or_not_auth(
    db: Session, slug: str, current_user: Optional[User] = None
) -> Article or None:
    """Get single Article or None on slug.
    Auth is optional."""
    articles = db.query(Article).where(Article.slug == slug).all()
    if not articles:
        return None
    articles = add_tags_authors_favorites_time_in_articles(db, articles)
    if current_user:
        articles = add_favorited(db, articles, current_user)
        for article in articles:
            subscribe = check_subscribe(
                db, current_user.username, article.author.username
            )
            if subscribe:
                article.author.following = True
    db.close()
    return articles[0]


def change_article(
    db: Session, slug: str, article_data: schemas.UpdateArticle, user: User
) -> Article:
    """Edit Article by slug."""
    up_article = (
        update(Article)
        .where(Article.slug == slug)
        .values(author=user.username, **article_data.article.dict(exclude_unset=True))
        .execution_options(synchronize_session="fetch")
    )
    db.execute(up_article)
    db.commit()
    db.close()
    article = get_single_article_auth_or_not_auth(db, slug)
    return article


def delete_article(db: Session, slug: str):
    """Delete Article by slug."""
    del_article = (
        delete(Article)
        .where(Article.slug == slug)
        .execution_options(synchronize_session="fetch")
    )
    db.execute(del_article)
    db.commit()


def get_comments(
    db: Session, slug: str, auth_user: Optional[User] = None
) -> List[Comment]:
    """Get article comments on slug.
    Auth is optional."""
    comments = db.query(Comment).where(Comment.article == slug).all()
    for comment in comments:
        comment.author = db.query(User).where(User.id == comment.author).first()
        if auth_user:
            comment.author = user_utils.add_following(db, comment.author, auth_user)
        comment.createdAt = comment.created_at
        comment.updatedAt = comment.updated_at
    return comments


def create_comment(
    db: Session, data: schemas.CreateComment, slug: str, user: User
) -> Comment:
    """Create a comment for an article by slug and user."""
    db_comment = Comment(body=data.comment.body, author=user.id, article=slug)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    db_comment.author = user
    db_comment.createdAt = db_comment.created_at
    db_comment.updatedAt = db_comment.updated_at
    return db_comment


def delete_comment(db: Session, slug: str, id: str, user: User):
    """Delete the comment on slug and the author of the article."""
    del_comment = (
        delete(Comment)
        .where(Comment.article == slug, Comment.id == id)
        .execution_options(synchronize_session="fetch")
    )
    db.execute(del_comment)
    db.commit()


def get_comment(db: Session, slug: str, id: str) -> Comment:
    """Get single comment for an article by slug and id comment."""
    comment = db.query(Comment).where(Comment.article == slug, Comment.id == id).first()
    return comment


def create_favorite(db: Session, slug: str, user: User):
    """Create Favorite model by article slug."""
    favorite = Favorite(article=slug, user=user.username)
    db.add(favorite)
    db.commit()


def delete_favorite(db: Session, slug: str, user: User):
    """Delete Favorite model by article slug and user."""
    del_favorite = (
        delete(Favorite)
        .where(Favorite.article == slug, Favorite.user == user.username)
        .execution_options(synchronize_session="fetch")
    )
    db.execute(del_favorite)
    db.commit()


def select_tags(db: Session) -> List[str]:
    """Get all tags."""
    db_tags = db.query(Tag).all()
    tags = [tag.name for tag in db_tags]
    return tags
