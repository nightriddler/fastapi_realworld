from fastapi import HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED

from src.db import models
from src.db.database import get_db
from src.router_setting import APIRouter
from src.users import utils

from . import authorize, crud, schemas

router_user = APIRouter()


@router_user.post(
    "/users/login",
    response_model=schemas.UserResponse,
    tags=["User and Authentication"],
)
async def authentication(
    user_login: schemas.LoginUserRequest, db: AsyncSession = Depends(get_db)
):
    """
    Login for existing user.
    """
    token = authorize.encode_jwt(user_login.user.email, user_login.user.password)
    user = await crud.get_user_by_token(db, token)
    if user:
        return schemas.UserResponse(user=user)
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authorized")


@router_user.post(
    "/users",
    response_model=schemas.UserResponse,
    status_code=201,
    tags=["User and Authentication"],
)
async def register_user(
    new_user: schemas.NewUserRequest, db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    """
    db_user_email = await crud.get_user_by_email(db, new_user.user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_username = await crud.get_user_by_username(db, new_user.user.username)
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = await crud.create_user(db, new_user)
    return schemas.UserResponse(user=user)


@router_user.get(
    "/user", response_model=schemas.UserResponse, tags=["User and Authentication"]
)
async def current_user(user: models.User = Depends(crud.get_curr_user_by_token)):
    """
    Gets the currently logged-in user.
    """
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authorized")
    return schemas.UserResponse(user=user)


@router_user.put(
    "/user", response_model=schemas.UpdateUserRequest, tags=["User and Authentication"]
)
async def update_user(
    data: schemas.UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(crud.get_curr_user_by_token),
):
    """
    Updated user information for current user.
    """
    if user:
        new_user = await crud.change_user(db, user, data)
        return schemas.UpdateUserRequest(user=new_user)
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authorized")


@router_user.get(
    "/profiles/{username}", response_model=schemas.ProfileUserResponse, tags=["Profile"]
)
async def get_profile(
    request: Request, username: str, db: AsyncSession = Depends(get_db)
):
    """
    Get a profile of a user of the system.
    Auth is optional.
    """
    profile_user = await crud.get_user_by_username(db, username)
    if not profile_user:
        raise HTTPException(status_code=400, detail="User not found")
    authorization = request.headers.get("authorization")
    if authorization:
        token = authorize.clear_token(authorization)
        current_user = await crud.get_curr_user_by_token(db, token)
        if current_user.username != profile_user.username:
            profile_user = await utils.add_following(db, profile_user, current_user)
    return schemas.ProfileUserResponse(profile=profile_user)


@router_user.post(
    "/profiles/{username}/follow",
    response_model=schemas.ProfileUserResponse,
    tags=["Profile"],
)
async def create_follow(
    username: str,
    db: AsyncSession = Depends(get_db),
    follower: models.User = Depends(crud.get_curr_user_by_token),
):
    """
    Follow a user by username.
    """
    following = await crud.get_user_by_username(db, username)
    if not following:
        raise HTTPException(status_code=400, detail="User not found")
    if follower == following:
        raise HTTPException(status_code=400, detail="You cannot subscribe to yourself")
    subscribe = await crud.check_subscribe(db, follower.username, following.username)
    if subscribe:
        raise HTTPException(status_code=400, detail="You are already a subscribed user")
    await crud.create_subscribe(
        db, user_username=follower.username, author_username=following.username
    )
    following.following = True
    return schemas.ProfileUserResponse(profile=following)


@router_user.delete(
    "/profiles/{username}/follow",
    response_model=schemas.ProfileUserResponse,
    tags=["Profile"],
)
async def delete_follow(
    username: str,
    db: AsyncSession = Depends(get_db),
    follower: models.User = Depends(crud.get_curr_user_by_token),
):
    """
    Unfollow a user by username.
    """
    following = await crud.get_user_by_username(db, username)
    if not following:
        raise HTTPException(status_code=400, detail="User not found")
    subscribe = await crud.check_subscribe(db, follower.username, following.username)
    if not subscribe:
        raise HTTPException(
            status_code=400, detail="You are not a subscribed this user"
        )
    await crud.delete_subscribe(
        db, user_username=follower.username, author_username=following.username
    )
    return schemas.ProfileUserResponse(profile=following)
