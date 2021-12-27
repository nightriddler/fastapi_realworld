from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.status import HTTP_401_UNAUTHORIZED

from src.db.database import get_db
from src.db.models import Follow, User
from src.users import authorize, schemas


async def get_curr_user_by_token(
    db: AsyncSession = Depends(get_db), token: str = Depends(authorize.check_token)
) -> User:
    """
    Getting a User model from a token and checking that the user exists.
    """
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authorized")
    return user


async def get_user_by_token(db: AsyncSession, token: int) -> User:
    """
    Get User model by token.
    """
    user = await db.execute(select(User).filter(User.token == token))
    return user.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> User:
    """
    Get User model by username.
    """
    user = await db.execute(select(User).filter(User.username == username))
    return user.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> User:
    """
    Get User model by email.
    """
    user = await db.execute(select(User).filter(User.email == email))
    return user.scalars().first()


async def create_user(db: AsyncSession, user: schemas.NewUserRequest) -> User:
    """
    Create and return a created User model.
    """
    db_user = User(
        token=authorize.encode_jwt(user.user.email, user.user.password),
        username=user.user.username,
        email=user.user.email,
        password=user.user.password,
        bio="default",
        image="default",
    )
    db.add(db_user)
    await db.commit()
    return db_user


async def change_user(
    db: AsyncSession, user: schemas.UserResponse, data: schemas.UserResponse
) -> User:
    """
    Update and return User model.
    """
    up_user = (
        update(User)
        .where(User.token == user.token)
        .values(**data.user.dict(exclude_unset=True))
    )
    await db.execute(up_user)
    await db.commit()
    return user


async def create_subscribe(db: AsyncSession, user_username: str, author_username: str):
    """
    Create Follow model by user and author username.
    The function does not return anything.
    """
    db_subscribe = Follow(user=user_username, author=author_username)
    db.add(db_subscribe)
    await db.commit()


async def delete_subscribe(db: AsyncSession, user_username: str, author_username: str):
    """
    Delete Follow model by user and author username.
    The function does not return anything.
    """
    subscribe = delete(Follow).where(
        Follow.user == user_username, Follow.author == author_username
    )
    await db.execute(subscribe)
    await db.commit()


async def check_subscribe(db: AsyncSession, follower: str, following: str) -> bool:
    """
    Checking Follow model by user and author username.
    Returns True if Follow model is found.
    """
    check = await db.execute(
        select(Follow).filter(Follow.user == follower, Follow.author == following)
    )
    check = check.scalars().first()
    return True if check else False
