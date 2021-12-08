# FastAPI Realworld

[![logo](https://user-images.githubusercontent.com/75097575/142890407-28f56df1-8c74-4086-a6ee-3ba7626ba154.png)](https://github.com/gothinkster/realworld)

[![build](https://img.shields.io/github/workflow/status/nightriddler/fastapi_realworld/RealWorld_fastapi%20workflow)](https://github.com/nightriddler/fastapi_realworld/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![license MIT](https://img.shields.io/github/license/nightriddler/fastapi_realworld)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi&logoColor=white&color=ff1709&labelColor=gray)](https://fastapi.tiangolo.com//)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-005?style=flat-square)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-0001?style=flat-square)](https://pydantic-docs.helpmanual.io/)

Implementation for [RealWorld](https://github.com/gothinkster/realworld) project using FastAPI and SQLAlchemy.


## Project deployment in Docker
1. Clone repository 
```
git clone https://github.com/nightriddler/fastapi_realworld.git
```
2. In the root folder create a file ``.env`` with environment variables:
```
SECRET=ff4c1a100618949dfb5cf50ecf05cba7ab6431f90ab045fe
ALGORITHM=HS256

DB_DIALECT=postgresql
DB_DRIVER=psycopg2
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_NAME=postgres

PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres

DB_TEST_DIALECT=postgresql
DB_TEST_DRIVER=psycopg2
DB_TEST_USERNAME=postgres
DB_TEST_PASSWORD=postgres
DB_TEST_HOST=db
DB_TEST_NAME=test
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

## Testing
When deployed in docker-compose, you can run Pytest:
```
docker-compose exec web python -m pytest
```
>The script `create_test_db.sh` automatically creates a database for testing using `POSTGRES_USER` and `POSTGRES_DB` from the environment. The name for the database can be set in the environment in the field `DB_TEST_NAME`.


## Documentation
The documentation `/docs/openapi.yml` can be seen at https://editor.swagger.io/ and also when you start the project at `http://127.0.0.1:8000/docs/`.


## Contact the author
>[LinkedIn](http://linkedin.com/in/aizi)

>[Telegram](https://t.me/nightriddler)

>[Portfolio](https://github.com/nightriddler)
