from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime
from .database import Base
from sqlalchemy.schema import Table


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True)
    email = Column(String(50), unique=True)
    username = Column(String(50), unique=True)
    bio = Column(Text)
    image = Column(String(250))
    password = Column(String(250))

    articles = relationship(
        'Article', cascade='all,delete-orphan', backref='authors')
    comments = relationship(
        'Comment', cascade='all,delete-orphan', backref='authors')
    favorites = relationship(
        'Favorite', cascade='all,delete-orphan', backref='users')

    def __repr__(self):
        return f'User(email={self.email},username={self.username})'


class Follow(Base):
    __tablename__ = 'followers'

    id = Column(Integer, primary_key=True)
    user = Column(
        String(50), ForeignKey('users.username', ondelete='CASCADE'))
    author = Column(
        String(50), ForeignKey('users.username', ondelete='CASCADE'))

    UniqueConstraint('user', 'author')

    followers = relationship(
        'User',
        foreign_keys=[user],
        backref=backref('follower_user', cascade='all,delete-orphan'))
    followings = relationship(
        'User',
        foreign_keys=[author],
        backref=backref('following_user', cascade='all,delete-orphan'))

    def __repr__(self):
        return f'Follow(user={self.user},author={self.author})'


article_tag_table = Table(
    'article_tag', Base.metadata,
    Column('article_id', ForeignKey('articles.id', ondelete='CASCADE')),
    Column('tags_name', ForeignKey('tags.name', ondelete='CASCADE')),
    UniqueConstraint('article_id', 'tags_name'))


user_article_table = Table(
    'user_article', Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE')),
    Column('article_id', ForeignKey('articles.id', ondelete='CASCADE')),
    UniqueConstraint('user_id', 'article_id'))


class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    slug = Column(String(100), unique=True)
    title = Column(String(100))
    description = Column(Text)
    body = Column(Text)
    author = Column(String(50), ForeignKey(
        'users.username', ondelete='CASCADE'))

    createdAt = Column(DateTime, default=datetime.now().isoformat())
    updatedAt = Column(
        DateTime,
        onupdate=datetime.now().isoformat(),
        default=datetime.now().isoformat())

    tag = relationship('Tag', secondary=article_tag_table)
    favorite = relationship(
        'Favorite', cascade='all,delete-orphan', backref='articles')

    def __repr__(self):
        return f'Article(slug={self.slug},title={self.title})'


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __repr__(self):
        return f'Tag(id={self.id},name={self.name})'


class Favorite(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True)
    user = Column(
        String(50), ForeignKey('users.username', ondelete='CASCADE'))
    article = Column(
        String(100), ForeignKey('articles.slug', ondelete='CASCADE'))

    def __repr__(self):
        return f'Favorite(article={self.article},user={self.user})'


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    body = Column(Text)
    author = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    article = Column(
        String(100), ForeignKey('articles.slug', ondelete='CASCADE'))
    createdAt = Column(DateTime, default=datetime.now().isoformat())
    updatedAt = Column(
        DateTime,
        onupdate=datetime.now().isoformat(),
        default=datetime.now().isoformat())

    def __repr__(self):
        return f'Comment(article={self.article},author={self.author})'
