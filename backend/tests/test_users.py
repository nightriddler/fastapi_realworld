from src.db.models import User
import json
import copy
from .schemas import check_content_user


def test_user_create(client, db, data_first_user):
    """Create user test."""
    response = client.post("/users", json=data_first_user)
    count_user = db.query(User).count()
    content = response.json()
    assert response.status_code == 201, "Expected 201 code."
    check_content_user(content["user"], data_first_user)

    data_another_username = copy.deepcopy(data_first_user)
    data_another_username["user"]["username"] = "another_username"
    response_same_email = client.post("/users", json=data_another_username)
    assert (
        response_same_email.status_code == 400
    ), "A user is created with the same email."

    data_another_email = copy.deepcopy(data_first_user)
    data_another_email["user"]["email"] = "another@email.com"
    response_same_username = client.post("/users", json=data_another_email)
    assert (
        response_same_username.status_code == 400
    ), "A user is created with the same username."

    assert count_user == 1, "A user with the same data is created."


def test_login_user(add_first_user, client, data_first_user):
    """Test login for existing user."""
    data_random = {
        "user": {
            "email": "random@random.com",
            "password": "random_password",
        }
    }

    response = client.post("/users/login", json=data_first_user)

    content = response.json()
    assert response.status_code == 200, "Expected 200 code."
    check_content_user(content["user"], data_first_user)

    response_random_user = client.post("/users/login", json=data_random)
    assert (
        response_random_user.status_code == 401
    ), "Authorization is not available to unregistered users."


def test_current_user(token_first_user, client, data_first_user):
    """Test gets the currently logged-in user. Auth requeired."""
    response = client.get(
        "/user", headers={"Authorization": f"Token {token_first_user}"}
    )
    content = response.json()
    assert response.status_code == 200, "Expected 200 code."
    check_content_user(content["user"], data_first_user)

    response_fake_token = client.get(
        "/user", headers={"Authorization": "Token faketoken"}
    )
    assert response_fake_token.status_code == 401, "Invalid token."


def test_update_user(token_first_user, client):
    """Test updated user information for current user. Auth requeired."""
    check = {
        "user": {
            "email": "update@fixture.com",
            "token": "update_token",
            "username": "update_fixture",
            "bio": "update_bio",
            "image": "update_url_image",
        }
    }
    update_data_json = json.loads(json.dumps(check))
    response = client.put(
        "/user",
        headers={"Authorization": f"Token {token_first_user}"},
        json=update_data_json,
    )
    content = response.json()
    assert response.status_code == 200, "Expected 200 code."
    check_content_user(content["user"], update_data_json)

    response_fake_token = client.put(
        "/user",
        headers={"Authorization": "Token faketoken"},
        json=update_data_json,
    )
    assert response_fake_token.status_code == 401, "Invalid token."
