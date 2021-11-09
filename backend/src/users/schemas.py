from typing import Optional
from pydantic import BaseModel


class LoginUser(BaseModel):
    email: str
    password: str


class NewUser(LoginUser):
    username: str


class LoginUserRequest(BaseModel):
    user: LoginUser


class NewUserRequest(BaseModel):
    user: NewUser


class User(LoginUser):
    token: str
    username: str
    bio: str
    image: str

    class Config:
        orm_mode = True


class UserInResponse(BaseModel):
    email: str
    token: str
    username: str
    bio: str
    image: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserInResponse


class UpdateUser(BaseModel):
    email: Optional[str] = None
    token: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    image: Optional[str] = None

    class Config:
        orm_mode = True


class UpdateUserRequest(BaseModel):
    user: Optional[UpdateUser] = None


class ProfileUser(BaseModel):
    username: str
    bio: str
    image: str
    following: Optional[bool] = False

    class Config:
        orm_mode = True


class ProfileUserResponse(BaseModel):
    profile: ProfileUser
