from typing import AsyncGenerator, Dict, Tuple

import pytest
from settings import config
from slugify import slugify
from sqlalchemy import func
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.models import Favorite
from starlette.responses import Response

from .schemas import check_content_article

pytestmark = pytest.mark.asyncio


async def test_post_favorite(
    db: AsyncSession,
    client: AsyncGenerator,
    data_first_user: Dict[str, Dict[str, str]],
    token_first_user: str,
    data_first_article: Dict[str, Dict[str, str]],
    create_and_get_response_two_article: Tuple[Response],
) -> None:
    """
    Test favorite an article.
    Auth is required.
    """
    first_article, _ = create_and_get_response_two_article
    slug_first_article = first_article.json()["article"]["slug"]

    response_withot_auth = await client.post(
        f"/articles/{slug_first_article}/favorite",
    )
    assert response_withot_auth.status_code == 401, "Expected 401 code."

    response_fake_article = await client.post(
        "/articles/fakeslugarticle/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_fake_article.status_code == 400, "Expected 400 code."

    response = await client.post(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    content = response.json()
    stmt = await db.execute(func.count(Favorite.id))
    count_favorites = stmt.scalar()

    check_content_article(content["article"], data_first_article, data_first_user)

    assert response.status_code == 200, "Expected 200 code."
    assert (
        content["article"]["favorited"] is True
    ), "The status of the favorite article is not displayed in the favorited field."
    assert (
        content["article"]["favoritesCount"] == 1
    ), "Adding the article to favorites did not change the 'favoritesCount' field."
    assert count_favorites == 1, "The favorite article was not added to the database."

    count_favorites_from_redis = await config.redis_db.hget(
        "count_favorites", slugify(data_first_article["article"]["title"])
    )
    assert count_favorites == int(
        count_favorites_from_redis
    ), "The article was not saved in redis cache."

    response_double = await client.post(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_double.status_code == 400, "Expected 400 code."

    stmt = await db.execute(func.count(Favorite.id))
    count_favorites = stmt.scalar()

    assert (
        count_favorites == 1
    ), "A record with the same fields was created in the database."


async def test_remove_favorite(
    db: AsyncSession,
    client: AsyncGenerator,
    data_first_user: Dict[str, Dict[str, str]],
    token_first_user: str,
    data_first_article: Dict[str, Dict[str, str]],
    token_second_user: str,
    get_tags: str,
    create_and_get_response_two_article: Tuple[Response],
    data_second_article: Dict[str, Dict[str, str]],
) -> None:
    """
    Test unfavorite an article.
    Auth is required.
    """
    first_article, _ = create_and_get_response_two_article
    slug_first_article = first_article.json()["article"]["slug"]

    await client.post(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )

    response_another_user = await client.delete(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_second_user}"},
    )
    assert response_another_user.status_code == 400, "Expected 400 code."

    stmt = await db.execute(func.count(Favorite.id))
    count_favorites = stmt.scalar()

    assert count_favorites == 1, "Deleted article from the database by another user."

    response_withot_auth = await client.delete(
        f"/articles/{slug_first_article}/favorite",
    )
    assert response_withot_auth.status_code == 401, "Expected 401 code."

    stmt = await db.execute(func.count(Favorite.id))
    count_favorites = stmt.scalar()

    assert (
        count_favorites == 1
    ), "Deleted article from the database without authorization.."

    response_fake_article = await client.delete(
        "/articles/fakeslugarticle/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_fake_article.status_code == 400, "Expected 400 code."

    response = await client.delete(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response.status_code == 200, "Expected 200 code."

    stmt = await db.execute(func.count(Favorite.id))
    count_favorites = stmt.scalar()
    content = response.json()

    check_content_article(content["article"], data_first_article, data_first_user)
    assert count_favorites == 0, "The favorite article was not deleted to the database."

    count_favorites_from_redis = await config.redis_db.hget(
        "count_favorites", slugify(data_first_article["article"]["title"])
    )
    assert count_favorites == int(
        count_favorites_from_redis
    ), "The article was not delete in redis cache."

    response_double = await client.delete(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_double.status_code == 400, "Expected 400 code."
