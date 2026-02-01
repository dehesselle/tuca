import json
from enum import StrEnum, auto
from http import HTTPStatus

import requests
from pydantic import BaseModel, Field
from urlpath import URL

from cio.auth import get_token


class Method(StrEnum):
    # https://github.com/python/cpython/issues/115509#issuecomment-1946971056
    @staticmethod
    def _generate_next_value_(name, *args):
        return name.upper()

    GET = auto()
    POST = auto()
    DELETE = auto()


class ResponseHeader(BaseModel):
    # rate_limit_limit: str = Field(alias="X-Rate-Limit-Limit", default="")
    rate_limit_remaining: str = Field(alias="X-Rate-Limit-Remaining", default="")
    # rate_limit_reset: str = Field(alias="X-Rate-Limit-Reset", default="")


class DeleteResponse(BaseModel):
    id: str
    status: str
    startetAt: str
    completedAt: str
    resourceId: str
    resourceType: str


ValidStatusCodes = [
    HTTPStatus.OK,
    HTTPStatus.CREATED,
    HTTPStatus.ACCEPTED,
    HTTPStatus.NO_CONTENT,
    HTTPStatus.BAD_REQUEST,
    HTTPStatus.UNAUTHORIZED,
    HTTPStatus.FORBIDDEN,
    HTTPStatus.NOT_FOUND,
    HTTPStatus.METHOD_NOT_ALLOWED,
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.SERVICE_UNAVAILABLE,
]  # https://api.clouding.io/docs/#section/Introduction/Responses


class Clouding:
    def __init__(self):
        self.api_url = URL("https://api.clouding.io/v1")
        self.api_auth = {"X-API-KEY": get_token(None)}
        self.endpoint = ""
        self.response = requests.Response()
        self.response_header: ResponseHeader = None

    @property
    def is_status_ok(self) -> bool:
        try:
            if self.response.status_code in [
                HTTPStatus.OK,
                HTTPStatus.CREATED,
                HTTPStatus.ACCEPTED,
                HTTPStatus.NO_CONTENT,
            ]:
                return True
        except:
            pass
        return False

    @property
    def is_status_valid(self) -> bool:
        return self.response.status_code in ValidStatusCodes

    def _post_processing(self):
        if self.is_status_valid:
            self.response_header = ResponseHeader.model_validate(self.response.headers)
        else:
            self.response_header = ResponseHeader()
            # FIXME: rework error handling
            print("invalid HTTP status", self.response.status_code)
            exit(1)

    def get(self, endpoint: str, headers: dict = {}):
        self.endpoint = endpoint
        headers.update(self.api_auth)
        self.response = requests.get(self.api_url / endpoint, headers=headers)
        self._post_processing()

    def post(self, endpoint: str, payload: dict, headers: dict = {}):
        self.endpoint = endpoint
        headers.update(self.api_auth)
        self.response = requests.post(
            self.api_url / endpoint, data=json.dumps(payload), headers=headers
        )
        self._post_processing()

    def delete(self, endpoint: str, headers: dict = {}):
        self.endpoint = endpoint
        headers.update(self.api_auth)
        self.response = requests.delete(self.api_url / endpoint, headers=headers)
        self._post_processing()
