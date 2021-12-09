from src.db.models import Comment
from .schemas import check_content_comment


def test_post_comment(
    db,
    client,
    data_first_user,
    token_first_user,
    create_and_get_response_one_article,
    data_comment,
):
    """Test create a comment for an article. Auth is required."""
    response_fake_article = client.post(
        "/articles/fakeslugarticle/comments",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_comment,
    )
    count_comment = db.query(Comment).count()
    assert response_fake_article.status_code == 400, "Expected 400 code."
    assert (
        count_comment == 0
    ), "Added a comment to a non-existent article in the database."

    slug = create_and_get_response_one_article.json()["article"]["slug"]
    response_without_auth = client.post(
        f"/articles/{slug}/comments",
        json=data_comment,
    )
    assert response_without_auth.status_code == 401, "Expected 401 code."

    response = client.post(
        f"/articles/{slug}/comments",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_comment,
    )
    count_comment = db.query(Comment).count()

    content = response.json()
    assert response.status_code == 200, "Expected 200 code."
    assert count_comment == 1, "Comment not added in database."
    check_content_comment(content["comment"], data_comment, data_first_user)


def test_select_comment(
    db,
    client,
    data_second_user,
    token_first_user,
    token_second_user,
    create_follow,
    create_and_get_response_one_article,
    data_comment,
):
    """Test create a comment for an article. Auth is required."""
    slug = create_and_get_response_one_article.json()["article"]["slug"]
    # db.close()
    client.post(
        f"/articles/{slug}/comments",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_comment,
    )
    db.close()
    data_comment["comment"]["body"] = "second_comment"
    client.post(
        f"/articles/{slug}/comments",
        headers={"Authorization": f"Token {token_second_user}"},
        json=data_comment,
    )

    response_fake_article = client.get(
        "/articles/fakeslugarticle/comments",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response_fake_article.status_code == 400, "Expected 400 code."

    response = client.get(
        f"/articles/{slug}/comments",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    count_comment = db.query(Comment).count()

    content = response.json()
    assert response.status_code == 200, "Expected 200 code."
    assert (
        len(content["comments"]) == 2
    ), "Not all comments on an article are displayed."
    assert count_comment == 2, "Comments are not saved in the database."
    check_content_comment(content["comments"][1], data_comment, data_second_user)
    assert (
        content["comments"][1]["author"]["following"] is True
    ), "Subscription status is not displayed in the 'following' field"


def test_remove_comment(
    db,
    client,
    data_second_user,
    token_first_user,
    token_second_user,
    create_and_get_response_one_article,
    data_comment,
):
    """Test delete a comment for an article. Auth is required."""
    slug = create_and_get_response_one_article.json()["article"]["slug"]
    response_create_comment = client.post(
        f"/articles/{slug}/comments",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_comment,
    )

    comment_id = response_create_comment.json()["comment"]["id"]

    response_fake_article = client.delete(
        f"/articles/fakeslugarticle/comments/{comment_id}",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    count_comment = db.query(Comment).count()
    assert response_fake_article.status_code == 400, "Expected 400 code."
    assert (
        count_comment == 1
    ), "Removed a comment from the database for an article that does not exist."

    response_fake_comment_id = client.delete(
        f"/articles/{slug}/comments/2",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    count_comment = db.query(Comment).count()
    assert response_fake_comment_id.status_code == 400, "Expected 400 code."
    assert (
        count_comment == 1
    ), "Removed a comment from the database with an incorrect id."

    response_another_user = client.delete(
        f"/articles/{slug}/comments/{comment_id}",
        headers={"Authorization": f"Token {token_second_user}"},
    )
    count_comment = db.query(Comment).count()
    assert response_another_user.status_code == 400, "Expected 400 code."
    assert (
        count_comment == 1
    ), "Removed a comment from the database when queried not the author of the comment."

    response = client.delete(
        f"/articles/{slug}/comments/{comment_id}",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    assert response.status_code == 200, "Expected 200 code."
