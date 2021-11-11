from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import or_
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from src.db.models import Article, Tag, Comment, User, Favorite, Follow
from src.articles import schemas
from src.users import crud as crud_users
from sqlalchemy import update, delete
from slugify import slugify
from sqlalchemy.orm import contains_eager
from fastapi import HTTPException
from collections import Counter


def select_articles(
        db, tag, author, favorited, limit, offset) -> List[Article]:
    # Добавить сортировку по favorited при авторизации.
    if tag:
        query = db.query(
            Article).join(Article.tag).options(
                contains_eager(Article.tag)).filter(
                    or_(tag is None, Tag.name == tag),
                    or_(author is None, Article.author == author))
    else:
        query = db.query(
            Article).filter(
                or_(author is None, Article.author == author))
    articles = query.order_by(-Article.id).offset(offset).limit(limit).all()
    articles_favorites = db.query(Favorite).all()
    favorites = [article.article for article in articles_favorites]
    count_favorite_articles = Counter(favorites)
    for article in articles:
        article.author = article.authors
        article.tagList = [tag.name for tag in article.tag]
        if article.slug in count_favorite_articles:
            article.favorited = True
            article.favoritesCount = count_favorite_articles[article.slug]
    return articles


def create_article(
        db: Session,
        data: schemas.CreateArticleRequest,
        user: User) -> Article:
    tags = []
    if data.article.tagList:
        tags = [
            tag_name for tag_name in db.query(
                Tag).filter(
                    Tag.name.in_(data.article.tagList)).all()]
    db_article = Article(
        slug=slugify(data.article.title),
        title=data.article.title,
        description=data.article.description,
        body=data.article.body,
        author=user.username,
        tag=tags)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    db_article.tagList = [tag.name for tag in db_article.tag]
    return db_article


def get_single_article(db: Session, slug: str) -> Article:
    article = db.query(Article).where(Article.slug == slug).first()

    article.author = crud_users.get_user_by_username(db, article.author)
    article.tagList = [tag.name for tag in article.tag]

    favorite = db.query(Favorite).where(Favorite.article == slug).all()
    favorites = [article.article for article in favorite]
    count_favorite_articles = Counter(favorites)
    if slug in count_favorite_articles:
        article.favorited = True
        article.favoritesCount = count_favorite_articles[slug]
    return article


def change_article(
        db: Session,
        slug: str,
        article_data: schemas.UpdateArticle,
        user: User) -> Article:
    check = db.query(Article).where(Article.slug == slug).first()
    if check.author != user.username:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail='You are not the author of this article')
    up_article = update(
        Article).where(
            Article.slug == slug).values(
                **article_data.article.dict(
                    exclude_unset=True)).execution_options(
                        synchronize_session="fetch")
    db.execute(up_article)
    db.commit()
    article = get_single_article(db, slug)
    return article


def delete_article(db: Session, slug: str):
    del_article = delete(
        Article).where(
            Article.slug == slug).execution_options(
                synchronize_session="fetch")
    db.execute(del_article)
    db.commit()


def get_comments(db: Session, slug: str) -> List[Comment]:
    comments = db.query(Comment).where(Comment.article == slug).all()
    for comment in comments:
        comment.author = db.query(
            User).where(User.id == comment.author).first()
    return comments


def create_comment(
        db: Session,
        data: schemas.CreateComment,
        slug: str,
        user: User) -> Comment:
    db_comment = Comment(
        body=data.comment.body,
        author=user.id,
        article=slug)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, slug: str, id: str, user: User):
    comment = db.query(Comment).where(
        Comment.article == slug,
        Comment.author == user.id,
        Comment.id == id).first()
    if not comment:
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY)
    del_comment = delete(
        Comment).where(
            Comment.article == slug,
            Comment.id == id).execution_options(
                synchronize_session="fetch")
    db.execute(del_comment)
    db.commit()


def check_favorite(db: Session, slug: str, username: str) -> bool:
    check = db.query(
        Favorite).filter(
            Favorite.user == username,
            Favorite.article == slug)
    return db.query(check.exists()).scalar()


def create_favorite(db: Session, slug: str, user: User) -> Article:
    favorite = Favorite(
        article=slug,
        user=user.username
    )
    db.add(favorite)
    db.commit()
    article = get_single_article(db, slug)
    check_article_favorite = check_favorite(db, slug, user.username)
    if check_article_favorite:
        article.favorited = True
    return article


def delete_favorite(db: Session, slug: str, user: User):
    check_article_favorite = check_favorite(db, slug, user.username)
    if not check_article_favorite:
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY)
    del_favorite = delete(
        Favorite).where(
            Favorite.article == slug,
            Favorite.user == user.username).execution_options(
                synchronize_session="fetch")
    db.execute(del_favorite)
    db.commit()


def select_tags(db: Session) -> List[str]:
    db_tags = db.query(Tag).all()
    tags = [tag.name for tag in db_tags]
    return tags


def feed_article(
    db: Session,
        user: User,
        limit: int,
        offset: int) -> List[Article]:
    articles = db.query(Article).join(
        Follow,
        Follow.author == Article.author).where(
            Follow.user == user.username).offset(offset).limit(limit).all()
    for article in articles:
        article.author = article.authors
        article.tagList = [tag.name for tag in article.tag]
    return articles
