from fastapi.exceptions import HTTPException
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security
from starlette.status import HTTP_401_UNAUTHORIZED
from constaint import decsription_token
import jwt
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

SECRET = os.environ.get('SECRET')
ALGORITHM = os.environ.get('ALGORITHM')

api_key_header = APIKeyHeader(
    scheme_name='Token',
    name='Authorization',
    description=decsription_token,
    auto_error=False)


def clear_token(token):
    try:
        split_token = token.split()
    except AttributeError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED)
    if len(split_token) == 2:
        scheme, credentials = split_token
        if scheme == 'Token':
            return credentials
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED)


def encode_jwt(email, password):
    token_jwt = jwt.encode({email: password}, SECRET, algorithm=ALGORITHM)
    return token_jwt


def check_token(raw_token: str = Security(api_key_header)):
    return clear_token(raw_token)
