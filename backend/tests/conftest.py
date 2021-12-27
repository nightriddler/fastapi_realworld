import asyncio
from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import wraps
from typing import AsyncGenerator, Callable, Dict, Generator, List, Tuple

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from settings import config
from src.db.database import create_engine_async_app
from src.db.models import Tag


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an instance of the default event loop for each test case.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db() -> AsyncSession:
    engine, async_session = create_engine_async_app(config.sqlalchemy_db)
    async with engine.begin() as connection:
        async with async_session(bind=connection) as session:
            yield session
            await session.flush()
            await session.rollback()
        await connection.close()


@pytest.fixture(scope="function")
def override_get_db(db: AsyncSession) -> Callable:
    async def _override_get_db():
        yield db

    return _override_get_db


@pytest.fixture(scope="function")
def app(override_get_db: Callable) -> FastAPI:

    from src.db.database import get_db

    from ..main import app

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture(scope="function")
async def client(app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


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


@pytest.fixture(scope="function")
async def add_first_user(
    client: AsyncGenerator, data_first_user: Dict[str, Dict[str, str]]
) -> None:
    await client.post("/users", json=data_first_user)


@pytest.fixture(scope="function")
async def add_second_user(
    client: AsyncGenerator, data_second_user: Dict[str, Dict[str, str]]
) -> None:
    await client.post("/users", json=data_second_user)


@pytest.fixture(scope="function")
async def token_first_user(
    add_first_user: None,
    client: AsyncGenerator,
    data_first_user: Dict[str, Dict[str, str]],
) -> str:
    response = await client.post("/users/login", json=data_first_user)
    return response.json()["user"]["token"]


@pytest.fixture(scope="function")
async def token_second_user(
    add_second_user: None,
    client: AsyncGenerator,
    data_second_user: Dict[str, Dict[str, str]],
) -> str:
    response = await client.post("/users/login", json=data_second_user)
    return response.json()["user"]["token"]


@pytest.fixture(scope="function")
async def create_follow(
    client: AsyncGenerator,
    token_first_user: str,
    add_second_user: None,
    data_second_user: Dict[str, Dict[str, str]],
) -> None:
    await client.post(
        f"/profiles/{data_second_user['user']['username']}/follow",
        headers={"Authorization": f"Token {token_first_user}"},
    )


@pytest.fixture(scope="function")
async def get_tags() -> List[str]:
    return ["first_tag", "second_tag"]


@pytest.fixture(scope="function")
async def create_and_get_tags(db: AsyncSession) -> List[str]:
    list_tag_name = ["first_tag", "second_tag"]
    tags = [Tag(name=name_tag) for name_tag in list_tag_name]
    db.add_all(tags)
    await db.commit()
    yield list_tag_name
    await db.rollback()


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


@pytest.fixture(scope="function")
async def create_and_get_response_one_article(
    db: AsyncSession,
    client: AsyncGenerator,
    token_first_user: str,
    data_first_article: Dict[str, Dict[str, str]],
    create_and_get_tags: List[str],
) -> Response:
    first_tag, second_tag = create_and_get_tags
    data_first_article["article"]["tagList"] = [first_tag, second_tag]

    first_article = await client.post(
        "/articles",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_first_article,
    )
    yield first_article


@pytest.fixture(scope="function")
async def create_and_get_response_two_article(
    db: AsyncSession,
    client: AsyncGenerator,
    token_first_user: str,
    token_second_user: str,
    data_first_article: Dict[str, Dict[str, str]],
    data_second_article: Dict[str, Dict[str, str]],
    create_and_get_tags: List[str],
) -> Tuple[Response]:
    first_tag, second_tag = create_and_get_tags
    data_first_article["article"]["tagList"] = [first_tag, second_tag]

    first_article = await client.post(
        "/articles",
        headers={"Authorization": f"Token {token_first_user}"},
        json=data_first_article,
    )
    data_second_article["article"]["tagList"] = [first_tag]
    second_article = await client.post(
        "/articles",
        headers={"Authorization": f"Token {token_second_user}"},
        json=data_second_article,
    )
    yield first_article, second_article


@pytest.fixture
def data_comment() -> Dict[str, Dict[str, str]]:
    return {
        "comment": {
            "body": "first_comment",
        }
    }


def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise

    return wrapper


# aiothhp issues: 4324 https://github.com/aio-libs/aiohttp/issues/4324#issuecomment-733884349

_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(
    _ProactorBasePipeTransport.__del__
)
