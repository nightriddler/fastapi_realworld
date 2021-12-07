from slugify import slugify
from ..src.db.models import Article, Tag
from .schemas import check_content_article


def test_get_tags(db, client, create_and_get_tags):
    """Test get tags. Auth not required."""
    response = client.get("/tags")
    count_tags = db.query(Tag).count()

    assert response.status_code == 200, "Expected 200 code."
    assert count_tags == len(create_and_get_tags), "Tags not added database."
    assert (
        response.json()["tags"] == create_and_get_tags
    ), "A list of name tags is expected."


def test_set_up_article(
    db,
    client,
    data_first_user,
    token_first_user,
    data_first_article,
    token_second_user,
    data_second_article,
    create_and_get_tags,
):
    """Test create an article. Auth is required"""
    response = client.post(
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

    count_articles = db.query(Article).count()
    assert count_articles == 1, "The article was not saved in the database."

    response_same_data = client.post(
        "/articles",
        headers={"Authorization": f"Token {token_second_user}"},
        json=data_first_article,
    )
    assert (
        response_same_data.status_code == 400
    ), "Creating an article with the same title."

    data_second_article["article"]["tagList"] = create_and_get_tags
    response_second_article = client.post(
        "/articles",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_second_article,
    )
    assert response_second_article.status_code == 201, "Expected 201 code."

    content_second_article = response_second_article.json()
    assert content_second_article["article"]["tagList"] == create_and_get_tags

    count_articles = db.query(Article).count()
    assert count_articles == 2, "The article was not saved in the database."


def test_get_articles(
    db,
    client,
    data_first_user,
    data_second_user,
    token_first_user,
    data_first_article,
    data_second_article,
    create_and_get_tags,
    create_and_get_response_two_article,
    create_follow,
):
    """Test get most recent articles globally.
    Use query parameters to filter results. Auth is optional."""

    first_article, second_article = create_and_get_response_two_article
    first_tag, second_tag = create_and_get_tags

    count_articles = db.query(Article).count()
    assert count_articles == 2, "The articles was not saved in the database."

    response_all_article = client.get(
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

    response_by_tag = client.get(
        f"/articles/?tag={second_tag}",
    )
    content = response_by_tag.json()
    check_content_article(content["articles"][0], data_first_article, data_first_user)
    assert content["articlesCount"] == 1, "Tag selection does not work."
    assert second_tag in content["articles"][0]["tagList"]

    author_article = data_second_user["user"]["username"]
    response_by_author = client.get(
        f"/articles/?author={author_article}",
        headers={"Authorization": f"Token {token_first_user}"},
    )
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
    client.post(
        f"/articles/{slug_first_article}/favorite",
        headers={"Authorization": f"Token {token_first_user}"},
    )

    favorite_user = data_first_user["user"]["username"]
    response_by_favorite = client.get(
        f"/articles/?favorited={favorite_user}",
        headers={"Authorization": f"Token {token_first_user}"},
    )
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

    response_by_limit = client.get("/articles/?limit=1")
    assert (
        response_by_limit.json()["articles"][0]["title"]
        == data_first_article["article"]["title"]
    ), "Filtering by limit does not work."

    response_by_offset = client.get("/articles/?offset=1")
    assert (
        response_by_offset.json()["articles"][0]["title"]
        == data_second_article["article"]["title"]
    ), "Filtering by offset does not work."


def test_get_recent_articles_from_users_you_follow(
    client,
    data_second_user,
    token_first_user,
    create_and_get_response_two_article,
    data_second_article,
    create_follow,
):
    """Test get most recent articles from users you follow.
    Use query parameters to limit. Auth is required."""
    response_feed = client.get(
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


def test_get_article(
    client,
    data_first_user,
    data_first_article,
    create_and_get_response_two_article,
):
    """Test get an article. Auth not required."""
    slug_article = slugify(data_first_article["article"]["title"])
    response_get_article = client.get(f"/articles/{slug_article}")
    content = response_get_article.json()
    assert response_get_article.status_code == 200, "Expected 200 code."
    check_content_article(content["article"], data_first_article, data_first_user)

    response_get_fakearticle = client.get("/articles/fakearticleslug")
    assert (
        response_get_fakearticle.status_code == 400
    ), "Expected 400 code for fakeslug."


def test_change_article(
    db,
    client,
    data_first_user,
    token_first_user,
    token_second_user,
    data_first_article,
    data_second_article,
    create_and_get_response_one_article,
):
    """Test update an article. Auth is required."""
    slug_article = slugify(data_first_article["article"]["title"])
    response_update_article = client.put(
        f"/articles/{slug_article}",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_second_article,
    )

    content = response_update_article.json()
    assert response_update_article.status_code == 200, "Expected 200 code."
    check_content_article(content["article"], data_second_article, data_first_user)

    response_update_article_without_auth = client.put(
        f"/articles/{slug_article}",
        json=data_second_article,
    )
    assert response_update_article_without_auth.status_code == 401, "Expected 401 code."

    response_update_article_another_user = client.put(
        f"/articles/{slug_article}",
        headers={"Authorization": f"Token {token_second_user}"},
        json=data_second_article,
    )
    assert response_update_article_another_user.status_code == 400, "Expected 400 code."


def test_remove_article(
    db,
    client,
    token_first_user,
    token_second_user,
    data_first_article,
    create_and_get_response_one_article,
):
    """Test delete an article. Auth is required."""
    count_article = db.query(Article).count()
    assert count_article == 1, "The article was not found in the database."

    slug_article = slugify(data_first_article["article"]["title"])

    response_remove_article_another_user = client.delete(
        f"/articles/{slug_article}",
        headers={"Authorization": f"Token {token_second_user}"},
    )
    count_article = db.query(Article).count()
    assert response_remove_article_another_user.status_code == 400, "Expected 400 code."
    assert count_article == 1, "The article can only be removed by the author."

    response_remove_article_without_auth = client.delete(f"/articles/{slug_article}")
    count_article = db.query(Article).count()
    assert response_remove_article_without_auth.status_code == 401, "Expected 401 code."
    assert count_article == 1, "Article deleted without authorization."

    response_remove_article = client.delete(
        f"/articles/{slug_article}",
        headers={"Authorization": f"Token {token_first_user}"},
    )
    count_article = db.query(Article).count()
    assert response_remove_article.status_code == 200, "Expected 200 code."
    assert count_article == 0, "The article is not removed from the database."
