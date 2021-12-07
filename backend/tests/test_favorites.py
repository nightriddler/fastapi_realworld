from ..src.db.models import Favorite
from .schemas import check_content_article


def test_post_favorite(
    db,
    client,
    data_first_user,
    token_first_user,
    data_first_article,
    create_and_get_response_two_article,
):
    """Test favorite an article. Auth is required."""
    first_article, second_article = create_and_get_response_two_article
    slug_first_article = first_article.json()["article"]["slug"]

    response_withot_auth = client.post(
        f"/articles/{slug_first_article}/favorite",
    )
    assert response_withot_auth.status_code == 401, "Expected 401 code."

    response_fake_article = client.post(
        "/articles/fakeslugarticle/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_fake_article.status_code == 400, "Expected 400 code."

    response = client.post(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    content = response.json()
    count_favorites = db.query(Favorite).count()

    check_content_article(content["article"], data_first_article, data_first_user)
    assert (
        content["article"]["favorited"] is True
    ), "The status of the favorite article is not displayed in the favorited field."
    assert (
        content["article"]["favoritesCount"] == 1
    ), "Adding the article to favorites did not change the 'favoritesCount' field."
    assert count_favorites == 1, "The favorite article was not added to the database."

    response_double = client.post(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    count_favorites = db.query(Favorite).count()
    assert response_double.status_code == 400, "Expected 400 code."
    assert (
        count_favorites == 1
    ), "A record with the same fields was created in the database."


def test_remove_favorite(
    db,
    client,
    data_first_user,
    token_first_user,
    data_first_article,
    token_second_user,
    create_and_get_response_two_article,
):
    """Test unfavorite an article. Auth is required."""
    first_article, second_article = create_and_get_response_two_article
    slug_first_article = first_article.json()["article"]["slug"]
    client.post(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )

    response_another_user = client.delete(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_second_user}"},
    )
    count_favorites = db.query(Favorite).count()
    assert response_another_user.status_code == 400, "Expected 400 code."
    assert count_favorites == 1, "Deleted article from the database by another user."

    response_withot_auth = client.delete(
        f"/articles/{slug_first_article}/favorite",
    )
    count_favorites = db.query(Favorite).count()
    assert response_withot_auth.status_code == 401, "Expected 401 code."
    assert (
        count_favorites == 1
    ), "Deleted article from the database without authorization.."

    response_fake_article = client.delete(
        "/articles/fakeslugarticle/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_fake_article.status_code == 400, "Expected 400 code."

    response = client.delete(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    count_favorites = db.query(Favorite).count()
    content = response.json()

    assert response.status_code == 200, "Expected 200 code."
    check_content_article(content["article"], data_first_article, data_first_user)
    assert count_favorites == 0, "The favorite article was not deleted to the database."

    response_double = client.delete(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_double.status_code == 400, "Expected 400 code."
