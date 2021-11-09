from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import or_
from src.db.models import Article, Tag
from src.articles import schemas
from src.db.models import User
from src.users import crud as crud_users
from sqlalchemy import update, delete
from slugify import slugify
from sqlalchemy.orm import contains_eager


def select_articles(
        db, tag, author, favorited, limit, offset) -> List[Article]:
    # Добавить сортировку по favorited.
    if tag:
        articles = db.query(
            Article).join(Article.tag).options(
                contains_eager(Article.tag)).filter(
                    or_(tag is None, Tag.name == tag),
                    or_(author is None, Article.author == author)
                    ).offset(offset).limit(limit).all()
    else:
        articles = db.query(
            Article).filter(
                or_(author is None, Article.author == author)).order_by(
                    -Article.id).offset(offset).limit(limit).all()
    return articles


def get_or_create_tags(
        db: Session,
        name: Optional[List[str]] = None) -> Optional[List[Tag]] == Tag:
    tags = db.query(
        Tag).filter(
            Tag.name.in_(name)).all()
    if tags:
        return [tag.name for tag in tags]
    create_tags = [Tag(name=name_tag) for name_tag in name]
    for tag in create_tags:
        db.add(tag)
        db.commit()
    name_tags = [tag.name for tag in create_tags]
    return name_tags


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
    return db_article


def get_single_article(db: Session, slug: str) -> Article:
    article = db.query(Article).where(Article.slug == slug).first()
    article.author = crud_users.get_user_by_username(db, article.author)
    return article


def change_article(
        db: Session,
        slug: str,
        article_data: schemas.UpdateArticle) -> Article:
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
