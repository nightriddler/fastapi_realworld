from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.users import crud


async def add_following(db: AsyncSession, user: User, follower: User) -> User:
    """
    Add a subscriber to the pydantic User model,
    if there is a Follow model.
    """
    subscribe = await crud.check_subscribe(db, follower.username, user.username)
    if subscribe:
        user.following = True
    return user
