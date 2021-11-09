from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import backref, relationship
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

    articles = relationship('Article', cascade='all,delete', backref='authors')
    comments = relationship('Comment', cascade='all,delete', backref='authors')
    favorites = relationship('Favorite', cascade='all,delete', backref='users')

    def __repr__(self):
        return f'User(email={self.email},username={self.username})'


class Follow(Base):
    __tablename__ = 'followers'

    id = Column(Integer, primary_key=True)
    user = Column(String(50), ForeignKey('users.username'))
    author = Column(String(50), ForeignKey('users.username'))

    followers = relationship(
        'User',
        foreign_keys=[user],
        backref=backref('follower_user', cascade='all,delete'))
    followings = relationship(
        'User',
        foreign_keys=[author],
        backref=backref('following_user', cascade='all,delete'))

    def __repr__(self):
        return f'Follow(user={self.user},author={self.author})'


article_tag_table = Table(
    'article_tag', Base.metadata,
    Column('article_id', ForeignKey('articles.id')),
    Column('tags_name', ForeignKey('tags.name')))


user_article_table = Table(
    'user_article', Base.metadata,
    Column('user_id', ForeignKey('users.id')),
    Column('article_id', ForeignKey('articles.id')))


class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    slug = Column(String(100), unique=True)
    title = Column(String(100))
    description = Column(Text)
    body = Column(Text)
    author = Column(String(50), ForeignKey('users.username'))

    tag = relationship('Tag', secondary=article_tag_table)
    favorite = relationship(
        'Favorite', cascade='all,delete', backref='articles')

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
    user = Column(String(50), ForeignKey('users.username'))
    article = Column(Integer, ForeignKey('articles.id'))

    def __repr__(self):
        return f'Favorite(article={self.article},user={self.user})'


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    body = Column(Text)
    author = Column(Integer, ForeignKey('users.id'))
    article = Column(Integer, ForeignKey('articles.id'))

    def __repr__(self):
        return f'Comment(article={self.article},author={self.author})'
