import os

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session
import pytest
from src.db.models import Tag

from src.db.database import Base
from ..main import app

from src.db.database import get_db
from fastapi.testclient import TestClient


load_dotenv(find_dotenv())

DB_TEST_DIALECT = os.environ.get("DB_TEST_DIALECT")
DB_TEST_DRIVER = os.environ.get("DB_TEST_DRIVER")
DB_TEST_USERNAME = os.environ.get("DB_TEST_USERNAME")
DB_TEST_PASSWORD = os.environ.get("DB_TEST_PASSWORD")
DB_TEST_HOST = os.environ.get("DB_TEST_HOST")
DB_TEST_NAME = os.environ.get("DB_TEST_NAME")


# SQLALCHEMY_DATABASE_URL = f"{DB_TEST_DIALECT}+{DB_TEST_DRIVER}://{DB_TEST_USERNAME}:{DB_TEST_PASSWORD}@{DB_TEST_HOST}/{DB_TEST_NAME}"

SQLALCHEMY_DATABASE_URL = (
    "postgresql+psycopg2://postgres:postgres@postgres:5432/postgres"
)


@pytest.fixture(scope="session")
def db_engine():
    print(SQLALCHEMY_DATABASE_URL)
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)

    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    connection.begin()

    db = Session(autocommit=False, autoflush=False, bind=connection)

    app.dependency_overrides[get_db] = lambda: db

    yield db

    db.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):

    with TestClient(app) as c:
        yield c


@pytest.fixture
def data_first_user():
    return {
        "user": {
            "email": "first@user.com",
            "password": "firsrt_password",
            "username": "first",
        }
    }


@pytest.fixture
def data_second_user():
    return {
        "user": {
            "email": "second@user.com",
            "password": "second_password",
            "username": "second",
        }
    }


@pytest.fixture
def add_first_user(client, data_first_user):
    client.post("/users", json=data_first_user)


@pytest.fixture
def add_second_user(client, data_second_user):
    client.post("/users", json=data_second_user)


@pytest.fixture
def token_first_user(add_first_user, client, data_first_user):
    response = client.post("/users/login", json=data_first_user)
    return response.json()["user"]["token"]


@pytest.fixture
def token_second_user(add_second_user, client, data_second_user):
    response = client.post("/users/login", json=data_second_user)
    return response.json()["user"]["token"]


@pytest.fixture
def create_follow(client, token_first_user, add_second_user, data_second_user):
    client.post(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )


@pytest.fixture
def create_and_get_tags(db):
    list_tag_name = ["first_tag", "second_tag"]
    tags = [Tag(name=name_tag) for name_tag in list_tag_name]
    db.add_all(tags)
    db.commit()
    yield list_tag_name


@pytest.fixture
def data_first_article():
    return {
        "article": {
            "title": "first_title",
            "description": "first_description",
            "body": "first_body",
        }
    }


@pytest.fixture
def data_second_article():
    return {
        "article": {
            "title": "second_title",
            "description": "second_description",
            "body": "second_body",
        }
    }


@pytest.fixture
def create_and_get_response_one_article(
    db,
    client,
    token_first_user,
    data_first_article,
    create_and_get_tags,
):
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
    db,
    client,
    token_first_user,
    token_second_user,
    data_first_article,
    data_second_article,
    create_and_get_tags,
):
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
def data_comment():
    return {
        "comment": {
            "body": "first_comment",
        }
    }
