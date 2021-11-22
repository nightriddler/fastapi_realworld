# Fastapi Realworld

[![build](https://img.shields.io/github/workflow/status/nightriddler/fastapi_realworld/RealWorld_fastapi%20workflow)](https://github.com/nightriddler/fastapi_realworld/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi&logoColor=white&color=ff1709&labelColor=gray)]((https://fastapi.tiangolo.com//))
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-005?style=flat-square)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-009?style=flat-square)](https://pydantic-docs.helpmanual.io/)

[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)

Implementation for [RealWorld](https://github.com/gothinkster/realworld) project using FastAPI and SQLAlchemy.

The project is under development.


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

PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_HOST=db

```
3. In the same folder, run docker-compose with the command 
```
docker-compose up
```
4. The project is available at
```
http://127.0.0.1:8000/docs/
```

## Contact the author
>[LinkedIn](http://linkedin.com/in/aizi)

>[Telegram](https://t.me/nightriddler)

>[Портфолио](https://github.com/nightriddler)
