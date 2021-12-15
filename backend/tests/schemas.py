import datetime
from typing import Dict


def check_content_article(
    content: Dict[str, Dict[str, str]],
    article: Dict[str, Dict[str, str]],
    author_article: Dict[str, Dict[str, str]],
) -> None:
    """Checking the form of the request response."""
    assert isinstance(content, dict)
    assert isinstance(content["slug"], str)
    assert content["title"] == article["article"]["title"]
    assert content["description"] == article["article"]["description"]
    assert content["body"] == article["article"]["body"]
    assert isinstance(content["tagList"], list)
    assert isinstance(
        datetime.datetime.strptime(content["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        datetime.datetime,
    )
    assert isinstance(
        datetime.datetime.strptime(content["updatedAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        datetime.datetime,
    )
    assert isinstance(content["favorited"], bool)
    assert isinstance(content["favoritesCount"], int)
    assert isinstance(content["author"], dict)
    assert content["author"]["username"] == author_article["user"]["username"]
    assert content["author"]["bio"]
    assert content["author"]["image"]
    assert isinstance(content["author"]["following"], bool)


def check_content_comment(
    content: Dict[str, Dict[str, str]],
    data_comment: Dict[str, Dict[str, str]],
    data_user: Dict[str, Dict[str, str]],
) -> None:
    """Checking the form of the request response."""
    assert isinstance(content, dict)
    assert isinstance(content["id"], int)
    assert isinstance(
        datetime.datetime.strptime(content["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        datetime.datetime,
    )
    assert isinstance(
        datetime.datetime.strptime(content["updatedAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        datetime.datetime,
    )
    assert content["body"] == data_comment["comment"]["body"]
    assert isinstance(content["author"], dict)
    assert content["author"]["username"] == data_user["user"]["username"]
    assert isinstance(content["author"]["bio"], str)
    assert isinstance(content["author"]["image"], str)
    assert isinstance(content["author"]["following"], bool)


def check_content_profile(
    content: Dict[str, str], following: Dict[str, Dict[str, str]]
) -> None:
    """Checking the form of the request response."""
    assert content["username"] == following["user"]["username"]
    assert isinstance(content["bio"], str)
    assert isinstance(content["image"], str)
    assert isinstance(content["following"], bool)


def check_content_user(
    content: Dict[str, str], user: Dict[str, Dict[str, str]]
) -> None:
    """Checking the form of the request response."""
    assert content["email"] == user["user"]["email"]
    assert content["username"] == user["user"]["username"]
    assert isinstance(content["token"], str)
    assert isinstance(content["bio"], str)
    assert isinstance(content["image"], str)
