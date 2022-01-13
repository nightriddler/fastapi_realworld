from typing import AsyncGenerator, Dict

import pytest
from sqlalchemy import func
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.models import Follow

from .schemas import check_content_profile

pytestmark = pytest.mark.asyncio


async def test_create_folllow(
    db: AsyncSession,
    client: AsyncGenerator,
    token_first_user: str,
    add_second_user: None,
    data_first_user: Dict[str, Dict[str, str]],
    data_second_user: Dict[str, Dict[str, str]],
) -> None:
    """
    Create subscribe.
    Auth requeired.
    """
    response = await client.post(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    content = response.json()
    assert response.status_code == 200, "Expected 200 code."
    check_content_profile(content["profile"], data_second_user)
    assert (
        content["profile"]["following"] is True
    ), "The user's subscription is not displayed."

    response_re_subscribe = await client.post(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert (
        response_re_subscribe.status_code == 400
    ), "You cannot subscribe twice to the same user."

    stmt = await db.execute(func.count(Follow.id))
    count_follow = stmt.scalar()
    assert (
        count_follow == 1
    ), "Repeated query with the same parameters, led to the creation of a string in the database."

    response_subscribe_for_yourself = await client.post(
        f"/profiles/{data_first_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert (
        response_subscribe_for_yourself.status_code == 400
    ), "You cannot sign up for yourself."

    stmt = await db.execute(func.count(Follow.id))
    count_follow = stmt.scalar()
    assert (
        count_follow == 1
    ), "I managed to create a subscription to myself in the base."

    response_fake_user = await client.post(
        "/profiles/fakeuser/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert (
        response_fake_user.status_code == 400
    ), "You can only subscribe to an existing user."

    stmt = await db.execute(func.count(Follow.id))
    count_follow = stmt.scalar()
    assert (
        count_follow == 1
    ), "I managed to create a subscription for a user that does not exist in the database."

    response_fake_token = await client.post(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": "Token faketoken"},
    )
    assert response_fake_token.status_code == 401, "Invalid token."

    stmt = await db.execute(func.count(Follow.id))
    count_follow = stmt.scalar()
    assert (
        count_follow == 1
    ), "It was possible to create a subscription with an invalid token."


async def test_get_profile(
    db: AsyncSession,
    client: AsyncGenerator,
    token_first_user: str,
    add_second_user: None,
    data_second_user: Dict[str, Dict[str, str]],
    create_follow: None,
) -> None:
    """
    Test get a profile of a user of the system.
    Auth is optional.
    """
    response_fake_token = await client.get(
        f"/profiles/{data_second_user['user']['username']}",
        headers={"Authorization": "Token faketoken"},
    )
    assert response_fake_token.status_code == 401, "Invalid token."
    response_fake_user = await client.get("/profiles/fakeuser")
    assert (
        response_fake_user.status_code == 400
    ), "You can only subscribe to an existing user."

    response_without_auth = await client.get(
        f"/profiles/{data_second_user['user']['username']}",
    )
    assert response_without_auth.status_code == 200, "Expected 200 code."

    content = response_without_auth.json()
    assert (
        response_without_auth.json()["profile"]["following"] is False
    ), "False to view the profile without logging in."
    check_content_profile(content["profile"], data_second_user)
    response_auth = await client.get(
        f"/profiles/{data_second_user['user']['username']}",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_auth.status_code == 200, "Expected 200 code."

    content = response_auth.json()
    assert (
        response_auth.json()["profile"]["following"] is True
    ), "The subscription does not appear when viewing a profile with a token."
    check_content_profile(content["profile"], data_second_user)


async def test_delete_follow(
    db: AsyncSession,
    client: AsyncGenerator,
    token_first_user: str,
    add_second_user: None,
    data_second_user: Dict[str, Dict[str, str]],
    create_follow: None,
) -> None:
    """
    Test unfollow a user by username.
    """
    response_fake_user = await client.delete(
        "/profiles/fakeuser/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_fake_user.status_code == 400, "User not found."

    response = await client.delete(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response.status_code == 200, "Expected 200 code."

    stmt = await db.execute(func.count(Follow.id))
    count_follow = stmt.scalar()

    content = response.json()
    assert count_follow == 0, "The subscription has not been removed from the database."
    check_content_profile(content["profile"], data_second_user)

    response_re_delete_subscribe = await client.delete(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert (
        response_re_delete_subscribe.status_code == 400
    ), "I managed to unsubscribe twice."
