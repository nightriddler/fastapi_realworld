from sqlalchemy.orm import Session

from src.db.models import User
from src.users import crud


def add_following(db: Session, user: User, follower: User) -> User:
    """Add a subscriber to the pydantic User model,
    if there is a Follow model."""
    subscribe = crud.check_subscribe(db, follower.username, user.username)
    if subscribe:
        user.following = True
    return user
