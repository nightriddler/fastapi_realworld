from sqlalchemy.orm import Session
from traitlets.traitlets import Bool
from src.users import schemas, authorize
from src.db.models import User, Follow
from sqlalchemy import update, delete
from fastapi.params import Depends
from src.db.database import get_db


def get_curr_user_by_token(
    db: Session = Depends(get_db),
    token: str = Depends(authorize.check_token)
) -> User:
    return get_user_by_token(db, token)


def get_user_by_token(db: Session, token: int) -> User:
    return db.query(User).filter(User.token == token).first()


def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: schemas.NewUserRequest) -> User:
    db_user = User(
        token=authorize.encode_jwt(user.user.email, user.user.password),
        username=user.user.username,
        email=user.user.email,
        password=user.user.password,
        bio='default',
        image='default')
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def change_user(
    db: Session,
    user: schemas.UserResponse,
    data: schemas.UserResponse
) -> User:
    up_user = update(
        User).where(
            User.token == user.token).values(
                **data.user.dict(
                    exclude_unset=True))
    db.execute(up_user)
    db.commit()
    curr_user = db.query(User).filter(User.token == user.token).first()
    return curr_user


def create_subscribe(db: Session, user_username: str, author_username: str):
    db_subscribe = Follow(
        user=user_username,
        author=author_username)
    db.add(db_subscribe)
    db.commit()


def delete_subscribe(db: Session, user_username: str, author_username: str):
    subscribe = delete(
        Follow).where(
            Follow.user == user_username,
            Follow.author == author_username)
    db.execute(subscribe)
    db.commit()


def check_subscribe(db: Session, follower: str, following: str) -> Bool:
    check = db.query(
        Follow).filter(
            Follow.user == follower,
            Follow.author == following)
    return db.query(check.exists()).scalar()
