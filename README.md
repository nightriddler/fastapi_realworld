# FastAPI Realworld

[![logo](https://user-images.githubusercontent.com/75097575/142890407-28f56df1-8c74-4086-a6ee-3ba7626ba154.png)](https://github.com/gothinkster/realworld)



[![Styles](https://img.shields.io/github/workflow/status/nightriddler/fastapi_realworld/Styles?label=Styles)](https://github.com/nightriddler/fastapi_realworld/actions/workflows/styles.yml)
[![Tests](https://img.shields.io/github/workflow/status/nightriddler/fastapi_realworld/Tests?label=Tests)](https://github.com/nightriddler/fastapi_realworld/actions/workflows/tests.yml)
[![codecov](https://codecov.io/github/nightriddler/fastapi_realworld/branch/main/graph/badge.svg?token=JQ4NUO1T4V)](https://codecov.io/github/nightriddler/fastapi_realworld)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![license MIT](https://img.shields.io/github/license/nightriddler/fastapi_realworld)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi&logoColor=white&color=ff1709&labelColor=gray)](https://fastapi.tiangolo.com//)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-005?style=flat-square)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-0001?style=flat-square)](https://pydantic-docs.helpmanual.io/)

Implementation for [RealWorld](https://github.com/gothinkster/realworld) project using FastAPI and SQLAlchemy.

Also:
```
fastapi
pydantic
sqlalchemy
alembic
asyncpg
asyncio
aioredis
pytest
httpx
```
> Redis for cache favorite articles and count favorite articles.

## Deployment in Docker
1. Clone repository 
```
git clone https://github.com/nightriddler/fastapi_realworld.git
```
2. In the root folder create a file `.env` with environment variables (or rename the file `.env.example` to `.env`)::
```
SECRET=secret-key
DATABASE_URL=postgresql+asyncpg2://postgres:postgres@db/postgres
REDIS_URL=redis://redis:6379
```
You can generate your `SECRET` with the command (from the root): 
```
echo SECRET=$(openssl rand -hex 32) >> .env
```
3. In the same folder, run docker-compose with the command 
```
docker-compose up
```
4. The project is available at
```
http://127.0.0.1:8000/docs/
```
The pgAdmin panel is available: 
```
http://127.0.0.1:5050/
```

## Testing in Docker
Run the migration to test it:
```
docker-compose exec web alembic upgrade head
```
And then, run the tests:
```
docker-compose exec web python -m pytest
```

## Deployment local
1. Clone repository 
```
git clone https://github.com/nightriddler/fastapi_realworld.git
```
2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/Scripts/activate 
```
3. Install go to the backend folder and install the dependencies:
```
cd backend/
pip install -r requirements.txt
```
4. Create a `.env` (you can use `.env.example`), with your `SECRET` and `DATABASE_URL` in the same backend folder.

5. Run the migrations:
```
alembic head upgrade
```
6. Run the application:
```
uvicorn main:app --reload
```
7. The app will be available at:
```
http://127.0.0.1:8000/docs
```
8. Running tests:
```
python -m pytest
```

## Documentation
The documentation `/docs/openapi.yml` can be seen at https://editor.swagger.io/ and also when you start the project at `http://127.0.0.1:8000/docs/`.


## Contact the author
>[LinkedIn](http://linkedin.com/in/aizi)

>[Telegram](https://t.me/nightriddler)

>[Portfolio](https://github.com/nightriddler)
