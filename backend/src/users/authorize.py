import os

import jwt
from constaint import decsription_token
from dotenv import find_dotenv, load_dotenv
from fastapi import Security
from fastapi.exceptions import HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

load_dotenv(find_dotenv())

SECRET = os.environ.get("SECRET")
ALGORITHM = os.environ.get("ALGORITHM")

api_key_header = APIKeyHeader(
    scheme_name="Token",
    name="Authorization",
    description=decsription_token,
    auto_error=False,
)


def clear_token(token):
    """Checks that the token has been transferred by form:
    Token xxxxxx.yyyyyyy.zzzzzz.
    Otherwise causes an exception."""
    try:
        split_token = token.split()
    except AttributeError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    if len(split_token) == 2:
        scheme, credentials = split_token
        if scheme == "Token":
            return credentials
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


def encode_jwt(email, password):
    """Create token by email and password."""
    token_jwt = jwt.encode({email: password}, SECRET, algorithm=ALGORITHM)
    return token_jwt


def check_token(raw_token: str = Security(api_key_header)):
    """Checking the token received from "Authorization" header.
    Returns a token."""
    return clear_token(raw_token)
