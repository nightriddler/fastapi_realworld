from typing import AsyncGenerator, Dict, List, Tuple

import pytest
from slugify import slugify
from sqlalchemy import func
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import Response
from starlette.testclient import TestClient

from src.db.models import Article, Tag

from .schemas import check_content_article

pytestmark = pytest.mark.asyncio


async def test_get_tags(
    db: AsyncSession, client: AsyncGenerator, create_and_get_tags: List[str]
) -> None:
    """
    Test get tags.
    Auth not required.
    """
    response = await client.get("/tags")

    stmt = await db.execute(func.count(Tag.id))
    count_tags = stmt.scalar()

    assert response.status_code == 200, "Expected 200 code."
    assert count_tags == len(create_and_get_tags), "Tags not added database."
    assert (
        response.json()["tags"] == create_and_get_tags
    ), "A list of name tags is expected."


async def test_set_up_article(
    db: AsyncSession,
    client: AsyncGenerator,
    data_first_user: Dict[str, Dict[str, str]],
    token_first_user: str,
    data_first_article: Dict[str, Dict[str, str]],
    token_second_user: str,
    data_second_article: Dict[str, Dict[str, str]],
    create_and_get_tags: List[str],
) -> None:
    """
    Test create an article.
    Auth is required.
    """
    response = await client.post(
        "/articles",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_first_article,
    )
    assert response.status_code == 201, "Expected 201 code."

    content = response.json()
    assert isinstance(content, dict)
    check_content_article(content["article"], data_first_article, data_first_user)
    assert content["article"]["favorited"] is False
    assert content["article"]["favoritesCount"] == 0
    assert content["article"]["author"]["following"] is False

    stmt = await db.execute(func.count(Article.id))
    count_articles = stmt.scalar()
    assert count_articles == 1, "The article was not saved in the database."

    response_same_data = await client.post(
        "/articles",
        headers={"Authorization": f"Token {token_second_user}"},
        json=data_first_article,
    )
    assert (
        response_same_data.status_code == 400
    ), "Creating an article with the same title."

    data_second_article["article"]["tagList"] = create_and_get_tags
    response_second_article = await client.post(
        "/articles",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_second_article,
    )
    assert response_second_article.status_code == 201, "Expected 201 code."

    content_second_article = response_second_article.json()
    assert content_second_article["article"]["tagList"] == create_and_get_tags

    stmt = await db.execute(func.count(Article.id))
    count_articles = stmt.scalar()
    assert count_articles == 2, "The article was not saved in the database."


async def test_get_articles(
    db: AsyncSession,
    client: AsyncGenerator,
    data_first_user: Dict[str, Dict[str, str]],
    data_second_user: Dict[str, Dict[str, str]],
    token_first_user: str,
    data_first_article: Dict[str, Dict[str, str]],
    data_second_article: Dict[str, Dict[str, str]],
    create_and_get_tags: List[str],
    create_and_get_response_two_article: Tuple[Response],
    create_follow: None,
) -> None:
    """
    Test get most recent articles globally.
    Use query parameters to filter results.

    Auth is optional.
    """
    first_article, _ = create_and_get_response_two_article
    _, second_tag = create_and_get_tags

    stmt = await db.execute(func.count(Article.id))
    count_articles = stmt.scalar()
    assert count_articles == 2, "The articles was not saved in the database."

    response_all_article = await client.get(
        "/articles", headers={"Authorization": f"Token {token_first_user}"}
    )
    content = response_all_article.json()
    assert response_all_article.status_code == 200, "Expected 200 code."
    check_content_article(content["articles"][0], data_first_article, data_first_user)
    assert (
        content["articlesCount"] == count_articles
    ), "Not all articles from the database are displayed."
    assert content["articlesCount"] == len(
        content["articles"]
    ), " The number of articles does not match the articlesCount field."

    response_by_tag = await client.get(
        f"/articles/?tag={second_tag}",
    )
    assert response_by_tag.status_code == 200, "Expected 200 code."

    content = response_by_tag.json()
    check_content_article(content["articles"][0], data_first_article, data_first_user)
    assert content["articlesCount"] == 1, "Tag selection does not work."
    assert second_tag in content["articles"][0]["tagList"]

    author_article = data_second_user["user"]["username"]
    response_by_author = await client.get(
        f"/articles/?author={author_article}",
        headers={"Authorization": f"Token {token_first_user}"},
    )

    assert response_by_author.status_code == 200, "Expected 200 code."
    content = response_by_author.json()
    check_content_article(content["articles"][0], data_second_article, data_second_user)
    assert content["articlesCount"] == 1, "Selecting by author does not work."
    assert (
        content["articles"][0]["author"]["username"] == author_article
    ), "Articles are not filtered by author."
    assert (
        content["articles"][0]["author"]["following"] is True
    ), "Subscriber status is not displayed in articles."

    slug_first_article = first_article.json()["article"]["slug"]
    await client.post(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )

    favorite_user = data_first_user["user"]["username"]
    response_by_favorite = await client.get(
        f"/articles/?favorited={favorite_user}",
        headers={"Authorization": f"Token {token_first_user}"},
    )

    assert response_by_favorite.status_code == 200, "Expected 200 code."
    content = response_by_favorite.json()
    check_content_article(content["articles"][0], data_first_article, data_first_user)
    assert (
        content["articles"][0]["favorited"] is True
    ), "The status of the favorite article is not displayed in the favorited field."
    assert (
        content["articles"][0]["author"]["username"] == favorite_user
    ), "Filtering by favorite username articles does not work."
    assert (
        content["articlesCount"] == 1
    ), "More articles are displayed than in the author's favorites."

    response_by_limit = await client.get("/articles/?limit=1")
    assert (
        response_by_limit.json()["articles"][0]["title"]
        == data_first_article["article"]["title"]
    ), "Filtering by limit does not work."

    response_by_offset = await client.get("/articles/?offset=1")
    assert (
        response_by_offset.json()["articles"][0]["title"]
        == data_second_article["article"]["title"]
    ), "Filtering by offset does not work."


async def test_get_recent_articles_from_users_you_follow(
    client: TestClient,
    data_second_user: Dict[str, Dict[str, str]],
    token_first_user: str,
    create_and_get_response_two_article: Tuple[Response],
    data_second_article: Dict[str, Dict[str, str]],
    create_follow: None,
) -> None:
    """
    Test get most recent articles from users you follow.
    Use query parameters to limit.

    Auth is required.
    """
    response_feed = await client.get(
        "/articles/feed", headers={"Authorization": f"Token {token_first_user}"}
    )
    content = response_feed.json()["articles"][0]
    check_content_article(content, data_second_article, data_second_user)
    assert response_feed.status_code == 200, "Excpected 200 code."
    assert (
        content["title"] == data_second_article["article"]["title"]
    ), "Articles on signed authors are not displayed."
    assert (
        content["author"]["following"] is True
    ), "Subscriber status is not displayed in article."


async def test_get_article(
    db: AsyncSession,
    client: AsyncGenerator,
    data_first_user: Dict[str, Dict[str, str]],
    data_first_article: Dict[str, Dict[str, str]],
    create_and_get_response_two_article: Tuple[Response],
) -> None:
    """
    Test get an article.
    Auth not required.
    """
    slug_article = slugify(data_first_article["article"]["title"])
    response_get_article = await client.get(f"/articles/{slug_article}")

    content = response_get_article.json()
    assert response_get_article.status_code == 200, "Expected 200 code."
    check_content_article(content["article"], data_first_article, data_first_user)

    response_get_fakearticle = await client.get("/articles/fakearticleslug")
    assert (
        response_get_fakearticle.status_code == 400
    ), "Expected 400 code for fakeslug."


async def test_change_article(
    db: AsyncSession,
    client: AsyncGenerator,
    data_first_user: Dict[str, Dict[str, str]],
    token_first_user: str,
    token_second_user: str,
    data_first_article: Dict[str, Dict[str, str]],
    data_second_article: Dict[str, Dict[str, str]],
    create_and_get_response_one_article: Tuple[Response],
) -> None:
    """
    Test update an article.
    Auth is required.
    """
    slug_article = slugify(data_first_article["article"]["title"])
    response_update_article = await client.put(
        f"/articles/{slug_article}",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_second_article,
    )
    assert response_update_article.status_code == 200, "Expected 200 code."

    content = response_update_article.json()
    check_content_article(content["article"], data_second_article, data_first_user)

    response_update_article_without_auth = await client.put(
        f"/articles/{slug_article}",
        json=data_second_article,
    )
    assert response_update_article_without_auth.status_code == 401, "Expected 401 code."

    response_update_article_another_user = await client.put(
        f"/articles/{slug_article}",
        headers={"Authorization": f"Token {token_second_user}"},
        json=data_second_article,
    )
    assert response_update_article_another_user.status_code == 400, "Expected 400 code."


async def test_remove_article(
    db: AsyncSession,
    client: AsyncGenerator,
    token_first_user: str,
    token_second_user: str,
    data_first_article: Dict[str, Dict[str, str]],
    create_and_get_response_one_article: Tuple[Response],
) -> None:
    """
    Test delete an article.
    Auth is required.
    """
    stmt = await db.execute(func.count(Article.id))
    count_articles = stmt.scalar()
    assert count_articles == 1, "The article was not found in the database."

    slug_article = slugify(data_first_article["article"]["title"])

    response_remove_article_another_user = await client.delete(
        f"/articles/{slug_article}",
        headers={"Authorization": f"Token {token_second_user}"},
    )

    stmt = await db.execute(func.count(Article.id))
    count_articles = stmt.scalar()

    assert response_remove_article_another_user.status_code == 400, "Expected 400 code."
    assert count_articles == 1, "The article can only be removed by the author."

    response_remove_article_without_auth = await client.delete(
        f"/articles/{slug_article}"
    )
    assert response_remove_article_without_auth.status_code == 401, "Expected 401 code."

    stmt = await db.execute(func.count(Article.id))
    count_articles = stmt.scalar()
    assert count_articles == 1, "Article deleted without authorization."

    response_remove_article = await client.delete(
        f"/articles/{slug_article}",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_remove_article.status_code == 200, "Expected 200 code."

    stmt = await db.execute(func.count(Article.id))
    count_articles = stmt.scalar()
    assert count_articles == 0, "The article is not removed from the database."
