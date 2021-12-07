from ..src.db.models import Follow
from .schemas import check_content_profile


def test_create_folllow(
    client, db, token_first_user, add_second_user, data_first_user, data_second_user
):
    """Create subscribe. Auth requeired."""
    response = client.post(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    content = response.json()
    assert response.status_code == 200, "Expected 200 code."
    check_content_profile(content["profile"], data_second_user)
    assert (
        content["profile"]["following"] is True
    ), "The user's subscription is not displayed."

    response_re_subscribe = client.post(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    count_follow = db.query(Follow).count()
    assert (
        response_re_subscribe.status_code == 400
    ), "You cannot subscribe twice to the same user."
    assert (
        count_follow == 1
    ), "Repeated query with the same parameters, led to the creation of a string in the database."

    response_subscribe_for_yourself = client.post(
        f"/profiles/{data_first_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    count_follow = db.query(Follow).count()
    assert (
        response_subscribe_for_yourself.status_code == 400
    ), "You cannot sign up for yourself."
    assert (
        count_follow == 1
    ), "I managed to create a subscription to myself in the base."

    response_fake_user = client.post(
        "/profiles/fakeuser/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    count_follow = db.query(Follow).count()
    assert (
        response_fake_user.status_code == 400
    ), "You can only subscribe to an existing user."
    assert (
        count_follow == 1
    ), "I managed to create a subscription for a user that does not exist in the database."

    response_fake_token = client.post(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": "Token faketoken"},
    )
    count_follow = db.query(Follow).count()
    assert response_fake_token.status_code == 401, "Invalid token."
    assert (
        count_follow == 1
    ), "It was possible to create a subscription with an invalid token."


def test_get_profile(
    db, client, token_first_user, add_second_user, data_second_user, create_follow
):
    """Test get a profile of a user of the system. Auth is optional."""
    response_fake_token = client.get(
        f"/profiles/{data_second_user['user']['username']}",
        headers={"Authorization": "Token faketoken"},
    )
    assert response_fake_token.status_code == 401, "Invalid token."

    response_fake_user = client.get("/profiles/fakeuser")
    assert (
        response_fake_user.status_code == 400
    ), "You can only subscribe to an existing user."

    response_without_auth = client.get(
        f"/profiles/{data_second_user['user']['username']}",
    )
    content = response_without_auth.json()
    assert response_without_auth.status_code == 200, "Expected 200 code."
    assert (
        response_without_auth.json()["profile"]["following"] is False
    ), "False to view the profile without logging in."
    check_content_profile(content["profile"], data_second_user)

    response_auth = client.get(
        f"/profiles/{data_second_user['user']['username']}",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    content = response_auth.json()
    assert response_auth.status_code == 200, "Expected 200 code."
    assert (
        response_auth.json()["profile"]["following"] is True
    ), "The subscription does not appear when viewing a profile with a token."
    check_content_profile(content["profile"], data_second_user)


def test_delete_follow(
    db, client, token_first_user, add_second_user, data_second_user, create_follow
):
    """Test unfollow a user by username."""

    response_fake_user = client.delete(
        "/profiles/fakeuser/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_fake_user.status_code == 400, "User not found."

    response = client.delete(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    count_follow = db.query(Follow).count()
    content = response.json()
    assert count_follow == 0, "The subscription has not been removed from the database."
    assert response.status_code == 200, "Expected 200 code."
    check_content_profile(content["profile"], data_second_user)

    response_re_delete_subscribe = client.delete(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert (
        response_re_delete_subscribe.status_code == 400
    ), "I managed to unsubscribe twice."
