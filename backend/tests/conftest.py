from typing import Dict, List, Tuple

import pytest
from fastapi.testclient import TestClient
from settings import config
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session
from src.db.database import get_db
from src.db.models import Tag
from starlette.responses import Response

from ..main import app


@pytest.fixture(scope="session")
def db_engine() -> Engine:
    engine = create_engine(config.sqlalchemy_db)
    yield engine


@pytest.fixture(scope="function")
def db(db_engine: Engine) -> Session:
    connection = db_engine.connect()
    connection.begin()

    db = Session(autocommit=False, autoflush=False, bind=connection)

    app.dependency_overrides[get_db] = lambda: db

    yield db

    db.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db: Session) -> TestClient:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def data_first_user() -> Dict[str, Dict[str, str]]:
    return {
        "user": {
            "email": "first@user.com",
            "password": "firsrt_password",
            "username": "first",
        }
    }


@pytest.fixture
def data_second_user() -> Dict[str, Dict[str, str]]:
    return {
        "user": {
            "email": "second@user.com",
            "password": "second_password",
            "username": "second",
        }
    }


@pytest.fixture
def add_first_user(
    client: TestClient, data_first_user: Dict[str, Dict[str, str]]
) -> None:
    client.post("/users", json=data_first_user)


@pytest.fixture
def add_second_user(
    client: TestClient, data_second_user: Dict[str, Dict[str, str]]
) -> None:
    client.post("/users", json=data_second_user)


@pytest.fixture
def token_first_user(
    add_first_user: None, client: TestClient, data_first_user: Dict[str, Dict[str, str]]
) -> str:
    response = client.post("/users/login", json=data_first_user)
    return response.json()["user"]["token"]


@pytest.fixture
def token_second_user(
    add_second_user: None,
    client: TestClient,
    data_second_user: Dict[str, Dict[str, str]],
) -> str:
    response = client.post("/users/login", json=data_second_user)
    return response.json()["user"]["token"]


@pytest.fixture
def create_follow(
    client: TestClient,
    token_first_user: str,
    add_second_user: None,
    data_second_user: Dict[str, Dict[str, str]],
) -> None:
    client.post(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )


@pytest.fixture
def create_and_get_tags(db: Session) -> List[str]:
    list_tag_name = ["first_tag", "second_tag"]
    tags = [Tag(name=name_tag) for name_tag in list_tag_name]
    db.add_all(tags)
    db.commit()
    yield list_tag_name


@pytest.fixture
def data_first_article() -> Dict[str, Dict[str, str]]:
    return {
        "article": {
            "title": "first_title",
            "description": "first_description",
            "body": "first_body",
        }
    }


@pytest.fixture
def data_second_article() -> Dict[str, Dict[str, str]]:
    return {
        "article": {
            "title": "second_title",
            "description": "second_description",
            "body": "second_body",
        }
    }


@pytest.fixture
def create_and_get_response_one_article(
    db: Session,
    client: TestClient,
    token_first_user: str,
    data_first_article: Dict[str, Dict[str, str]],
    create_and_get_tags: List[str],
) -> Response:
    first_tag, second_tag = create_and_get_tags
    data_first_article["article"]["tagList"] = [first_tag, second_tag]

    first_article = client.post(
        "/articles",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_first_article,
    )
    db.close
    return first_article


@pytest.fixture
def create_and_get_response_two_article(
    db: Session,
    client: TestClient,
    token_first_user: str,
    token_second_user: str,
    data_first_article: Dict[str, Dict[str, str]],
    data_second_article: Dict[str, Dict[str, str]],
    create_and_get_tags: List[str],
) -> Tuple[Response]:
    first_tag, second_tag = create_and_get_tags
    data_first_article["article"]["tagList"] = [first_tag, second_tag]

    first_article = client.post(
        "/articles",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_first_article,
    )
    db.close()
    data_second_article["article"]["tagList"] = [first_tag]
    second_article = client.post(
        "/articles",
        headers={"Authorization": f"Token {token_second_user}"},
        json=data_second_article,
    )
    db.close()
    return first_article, second_article


@pytest.fixture
def data_comment() -> Dict[str, Dict[str, str]]:
    return {
        "comment": {
            "body": "first_comment",
        }
    }
