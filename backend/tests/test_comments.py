from typing import AsyncGenerator, Dict

import pytest
from sqlalchemy import func
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import Response

from src.db.models import Comment

from .schemas import check_content_comment

pytestmark = pytest.mark.asyncio


async def test_post_comment(
    db: AsyncSession,
    client: AsyncGenerator,
    data_first_user: Dict[str, Dict[str, str]],
    token_first_user: str,
    create_and_get_response_one_article: Response,
    data_comment: Dict[str, Dict[str, str]],
) -> None:
    """
    Test create a comment for an article.
    Auth is required.
    """
    response_fake_article = await client.post(
        "/articles/fakeslugarticle/comments",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_comment,
    )
    assert response_fake_article.status_code == 400, "Expected 400 code."

    stmt = await db.execute(func.count(Comment.id))
    count_comment = stmt.scalar()
    assert (
        count_comment == 0
    ), "Added a comment to a non-existent article in the database."

    slug = create_and_get_response_one_article.json()["article"]["slug"]
    response_without_auth = await client.post(
        f"/articles/{slug}/comments",
        json=data_comment,
    )
    assert response_without_auth.status_code == 401, "Expected 401 code."

    response = await client.post(
        f"/articles/{slug}/comments",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_comment,
    )
    assert response.status_code == 200, "Expected 200 code."

    stmt = await db.execute(func.count(Comment.id))
    count_comment = stmt.scalar()

    content = response.json()
    assert count_comment == 1, "Comment not added in database."
    check_content_comment(content["comment"], data_comment, data_first_user)


async def test_select_comment(
    db: AsyncSession,
    client: AsyncGenerator,
    data_second_user: Dict[str, Dict[str, str]],
    token_first_user: str,
    token_second_user: str,
    create_follow: None,
    create_and_get_response_one_article: Response,
    data_comment: Dict[str, Dict[str, str]],
) -> None:
    """
    Test create a comment for an article.
    Auth is required.
    """
    slug = create_and_get_response_one_article.json()["article"]["slug"]
    await client.post(
        f"/articles/{slug}/comments",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_comment,
    )
    await db.close()
    data_comment["comment"]["body"] = "second_comment"
    await client.post(
        f"/articles/{slug}/comments",
        headers={"Authorization": f"Token {token_second_user}"},
        json=data_comment,
    )
    await db.close()
    response_fake_article = await client.get(
        "/articles/fakeslugarticle/comments",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_fake_article.status_code == 400, "Expected 400 code."

    response = await client.get(
        f"/articles/{slug}/comments",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response.status_code == 200, "Expected 200 code."

    stmt = await db.execute(func.count(Comment.id))
    count_comment = stmt.scalar()

    content = response.json()
    assert (
        len(content["comments"]) == 2
    ), "Not all comments on an article are displayed."
    assert count_comment == 2, "Comments are not saved in the database."
    check_content_comment(content["comments"][1], data_comment, data_second_user)
    assert (
        content["comments"][1]["author"]["following"] is True
    ), "Subscription status is not displayed in the 'following' field"


async def test_remove_comment(
    db: AsyncSession,
    client: AsyncGenerator,
    token_first_user: str,
    token_second_user: str,
    create_and_get_response_one_article: Response,
    data_comment: Dict[str, Dict[str, str]],
) -> None:
    """
    Test delete a comment for an article.
    Auth is required.
    """
    slug = create_and_get_response_one_article.json()["article"]["slug"]
    response_create_comment = await client.post(
        f"/articles/{slug}/comments",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_comment,
    )

    comment_id = response_create_comment.json()["comment"]["id"]
    await db.close()
    response_fake_article = await client.delete(
        f"/articles/fakeslugarticle/comments/{comment_id}",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_fake_article.status_code == 400, "Expected 400 code."

    stmt = await db.execute(func.count(Comment.id))
    count_comment = stmt.scalar()
    assert (
        count_comment == 1
    ), "Removed a comment from the database for an article that does not exist."

    response_fake_comment_id = await client.delete(
        f"/articles/{slug}/comments/2",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_fake_comment_id.status_code == 400, "Expected 400 code."

    stmt = await db.execute(func.count(Comment.id))
    count_comment = stmt.scalar()
    assert (
        count_comment == 1
    ), "Removed a comment from the database with an incorrect id."

    response_another_user = await client.delete(
        f"/articles/{slug}/comments/{comment_id}",
        headers={"Authorization": f"Token {token_second_user}"},
    )
    assert response_another_user.status_code == 400, "Expected 400 code."

    stmt = await db.execute(func.count(Comment.id))
    count_comment = stmt.scalar()
    assert (
        count_comment == 1
    ), "Removed a comment from the database when queried not the author of the comment."

    response = await client.delete(
        f"/articles/{slug}/comments/{comment_id}",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response.status_code == 200, "Expected 200 code."
