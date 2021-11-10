from typing import List, Optional
from pydantic import BaseModel
from src.users.schemas import ProfileUser
from datetime import datetime


class Article(BaseModel):
    slug: str
    title: str
    description: str
    body: str
    tagList: Optional[List[str]] = []
    createdAt: str = datetime.now().isoformat()
    updatedAt: str = datetime.now().isoformat()
    favorited: Optional[bool] = False
    favoritesCount: Optional[int] = 0
    author: ProfileUser

    class Config:
        orm_mode = True


class GetArticles(BaseModel):
    articles: List[Article]
    articlesCount: Optional[int] = 0

    class Config:
        orm_mode = True


class CreateArticle(BaseModel):
    title: str
    description: str
    body: str
    tagList: Optional[List[str]] = None


class CreateArticleRequest(BaseModel):
    article: CreateArticle


class CreateArticleResponse(BaseModel):
    article: Article


class GetArticle(BaseModel):
    article: Article

    class Config:
        orm_mode = True


class ChangeArticle(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None


class UpdateArticle(BaseModel):
    article: ChangeArticle


class Comment(BaseModel):
    id: int
    createdAt: str = datetime.now().isoformat()
    updatedAt: str = datetime.now().isoformat()
    body: str
    author: ProfileUser

    class Config:
        orm_mode = True


class GetCommentsResponse(BaseModel):
    comments: List[Comment]


class CreateCommentBody(BaseModel):
    body: str


class CreateComment(BaseModel):
    comment: CreateCommentBody


class GetCommentResponse(BaseModel):
    comment: Comment


class GetTags(BaseModel):
    tags: List[str]

    class Config:
        orm_mode = True
