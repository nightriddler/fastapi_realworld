from fastapi import HTTPException, APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from . import authorize, schemas, crud
from src.db import models
from src.db.database import get_db
from starlette.status import HTTP_401_UNAUTHORIZED


router_user = APIRouter()


@router_user.post(
    '/users',
    response_model=schemas.UserResponse,
    status_code=201,
    tags=['User and Authentication']
)
def register_user(
    new_user: schemas.NewUserRequest,
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_email(db, new_user.user.email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    user = crud.create_user(db, new_user)
    return schemas.UserResponse(user=user)


@router_user.post(
    '/users/login',
    response_model=schemas.UserResponse,
    tags=['User and Authentication']
)
def authentication(
        user_login: schemas.LoginUserRequest,
        db: Session = Depends(get_db)
):
    token = authorize.encode_jwt(
        user_login.user.email, user_login.user.password)
    user = crud.get_user_by_token(db, token)
    if user:
        return schemas.UserResponse(user=user)
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Not authorized")


@router_user.get(
    '/user',
    response_model=schemas.UserResponse,
    tags=['User and Authentication'])
def current_user(
        user: models.User = Depends(crud.get_curr_user_by_token)):
    return schemas.UserResponse(user=user)


@router_user.put(
    '/user',
    response_model=schemas.UpdateUserRequest,
    tags=['User and Authentication'])
def update_user(
        data: schemas.UpdateUserRequest,
        db: Session = Depends(get_db),
        user: models.User = Depends(crud.get_curr_user_by_token)):
    if user:
        new_user = crud.change_user(db, user, data)
        return schemas.UpdateUserRequest(user=new_user)
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Not authorized")


@router_user.get(
    '/profiles/{username}',
    response_model=schemas.ProfileUserResponse,
    tags=['Profile'])
def get_profile(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username)
    return schemas.ProfileUserResponse(profile=user)


@router_user.post(
    '/profiles/{username}/follow',
    response_model=schemas.ProfileUserResponse,
    tags=['Profile'])
def create_folllow(
        username: str,
        db: Session = Depends(get_db),
        follower: models.User = Depends(crud.get_curr_user_by_token)):
    following = crud.get_user_by_username(db, username)
    crud.create_subscribe(
        db,
        user_username=follower.username,
        author_username=following.username)
    subscribe = crud.check_subscribe(db, follower.username, following.username)
    if subscribe:
        following.following = True
    return schemas.ProfileUserResponse(profile=following)


@router_user.delete(
    '/profiles/{username}/follow',
    response_model=schemas.ProfileUserResponse,
    tags=['Profile']
)
def delete_follow(
        username: str,
        db: Session = Depends(get_db),
        follower: models.User = Depends(crud.get_curr_user_by_token)):
    following = crud.get_user_by_username(db, username)
    crud.delete_subscribe(
        db,
        user_username=follower.username,
        author_username=following.username)
    return schemas.ProfileUserResponse(profile=following)
