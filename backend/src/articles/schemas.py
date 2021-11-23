from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.users.schemas import ProfileUser


def convert_datetime_to_iso_8601(datetime: datetime) -> str:
    return datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class Article(BaseModel):
    slug: str
    title: str
    description: str
    body: str
    tagList: Optional[List[str]] = []
    createdAt: datetime
    updatedAt: datetime
    favorited: Optional[bool] = False
    favoritesCount: Optional[int] = 0
    author: ProfileUser

    class Config:
        orm_mode = True
        json_encoders = {datetime: convert_datetime_to_iso_8601}


class GetArticles(BaseModel):
    articles: List[Article]
    articlesCount: Optional[int] = 0

    class Config:
        orm_mode = True
        json_encoders = {datetime: convert_datetime_to_iso_8601}


class CreateArticle(BaseModel):
    title: str
    description: str
    body: str
    tagList: Optional[List[str]] = None


class CreateArticleRequest(BaseModel):
    article: CreateArticle


class CreateArticleResponse(BaseModel):
    article: Article

    class Config:
        json_encoders = {datetime: convert_datetime_to_iso_8601}


class GetArticle(BaseModel):
    article: Article

    class Config:
        orm_mode = True
        json_encoders = {datetime: convert_datetime_to_iso_8601}


class ChangeArticle(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None


class UpdateArticle(BaseModel):
    article: ChangeArticle


class Comment(BaseModel):
    id: int
    createdAt: datetime
    updatedAt: datetime
    body: str
    author: ProfileUser

    class Config:
        orm_mode = True
        json_encoders = {datetime: convert_datetime_to_iso_8601}


class GetCommentsResponse(BaseModel):
    comments: List[Comment]

    class Config:
        json_encoders = {datetime: convert_datetime_to_iso_8601}


class CreateCommentBody(BaseModel):
    body: str


class CreateComment(BaseModel):
    comment: CreateCommentBody

    class Config:
        json_encoders = {datetime: convert_datetime_to_iso_8601}


class GetCommentResponse(BaseModel):
    comment: Comment

    class Config:
        json_encoders = {datetime: convert_datetime_to_iso_8601}


class GetTags(BaseModel):
    tags: List[str]

    class Config:
        orm_mode = True
