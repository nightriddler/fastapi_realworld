from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import Table
from sqlalchemy.sql.sqltypes import DateTime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True)
    email = Column(String(50), unique=True)
    username = Column(String(50), unique=True)
    bio = Column(Text)
    image = Column(String(250))
    password = Column(String(250))

    articles = relationship(
        "Article",
        cascade="all,delete-orphan",
        backref="authors",
    )
    comments = relationship(
        "Comment",
        cascade="all,delete-orphan",
        backref="authors",
    )
    favorites = relationship(
        "Favorite",
        cascade="all,delete-orphan",
        backref="users",
    )

    def __repr__(self):
        return f"User(email={self.email},username={self.username})"


class Follow(Base):
    __tablename__ = "followers"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(Integer, primary_key=True)
    user = Column(String(50), ForeignKey("users.username", ondelete="CASCADE"))
    author = Column(String(50), ForeignKey("users.username", ondelete="CASCADE"))

    followers = relationship(
        "User",
        foreign_keys=[user],
        backref=backref("follower_user", cascade="all,delete-orphan"),
    )

    followings = relationship(
        "User",
        foreign_keys=[author],
        backref=backref("following_user", cascade="all,delete-orphan"),
    )

    def __repr__(self):
        return f"Follow(user={self.user},author={self.author})"


article_tag_table = Table(
    "article_tag",
    Base.metadata,
    Column("article_id", ForeignKey("articles.id", ondelete="CASCADE")),
    Column("tags_name", ForeignKey("tags.name", ondelete="CASCADE")),
)


class Article(Base):
    __tablename__ = "articles"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(Integer, primary_key=True)
    slug = Column(String(100), unique=True)
    title = Column(String(100))
    description = Column(Text)
    body = Column(Text)
    author = Column(String(50), ForeignKey("users.username", ondelete="CASCADE"))

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(
        DateTime,
        onupdate=datetime.now(),
        default=datetime.now(),
    )

    tag = relationship(
        "Tag",
        secondary=article_tag_table,
        backref="articles",
    )

    favorite = relationship(
        "Favorite",
        cascade="all,delete-orphan",
        backref="articles",
    )

    comments = relationship(
        "Comment",
        cascade="all,delete-orphan",
        backref="articles",
    )

    def __repr__(self):
        return f"Article(slug={self.slug},title={self.title})"


class Tag(Base):
    __tablename__ = "tags"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __repr__(self):
        return f"Tag(id={self.id},name={self.name})"


class Favorite(Base):
    __tablename__ = "favorites"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(Integer, primary_key=True)
    user = Column(String(50), ForeignKey("users.username", ondelete="CASCADE"))
    article = Column(String(100), ForeignKey("articles.slug", ondelete="CASCADE"))

    def __repr__(self):
        return f"Favorite(article={self.article},user={self.user})"


class Comment(Base):
    __tablename__ = "comments"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(Integer, primary_key=True)
    body = Column(Text)
    author = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    article = Column(String(100), ForeignKey("articles.slug", ondelete="CASCADE"))

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(
        DateTime,
        onupdate=datetime.now(),
        default=datetime.now(),
    )

    def __repr__(self):
        return f"Comment(article={self.article},author={self.author})"
