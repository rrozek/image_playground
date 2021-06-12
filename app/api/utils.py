import base64
import json
import os
import string
import logging
import sys
import typing

from aenum import Enum
from hashlib import sha256
from uuid import uuid4
from datetime import datetime, timedelta
from functools import lru_cache, wraps

from rest_framework.response import Response
from rest_framework import status as _status

from api.exceptions import ParamError

VALID_PIN_CHARACTERS = [s for s in string.digits]


def get_pretty_logger(prefix: str) -> logging.Logger:
    logger = logging.getLogger(prefix)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = get_pretty_logger('api.utils')

def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime
            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.name, x.value) for x in cls)

    @classmethod
    def _missing_name_(cls, name):
        for member in cls:
            if member.name.casefold() == name.casefold():
                return member


class ErrorCode(ChoiceEnum):
    Ok = 0
    MissingParams = 1
    InvalidParams = 2
    ExchangeLimitExceeded = 3
    NotFound = 4
    BadPin = 5
    Timeout = 6
    DataMismatch = 7

    DatabaseError = 100


def request_hash(request_data: dict) -> str:
    sha = sha256()
    sha.update(json.dumps(request_data, sort_keys=True).encode('utf-8'))
    return sha.hexdigest()


def session_token(request_data: dict) -> str:
    sha = sha256()
    sha.update(json.dumps(request_data, sort_keys=True).encode('utf-8'))
    sha.update(uuid4().hex.encode('utf-8'))
    return sha.hexdigest()


def source_hash(data: str) -> str:
    return sha256(data.encode('utf-8')).hexdigest()


def file_hash(filepath: str) -> str:
    with open(filepath, 'rb') as file:
        return sha256(file.read()).hexdigest()


def encode_base64(filepath: str) -> str:
    if not os.path.exists(filepath):
        errorstring = f'expected output file: {filepath} does not exist'
        logger.error(errorstring)
        raise ParamError(ErrorCode.NotFound, errorstring)
    with open(filepath, 'rb') as file:
        encoded = f'data:image/{filepath.split(".")[-1]};base64,'
        encoded = encoded + base64.b64encode(file.read()).decode('utf-8')
        return encoded


def xresponse(status=_status.HTTP_200_OK, error_code=ErrorCode.Ok, msg='', **kwargs) -> Response:
    common_response = {
        'result': 'success' if _status.is_success(status) else 'error',
        'error_code': error_code.value,
        'msg': msg,
        'data': {**kwargs}
    }
    return Response(common_response, status=status)
