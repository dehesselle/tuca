import json
from enum import StrEnum, auto
from http import HTTPStatus

import requests
from urlpath import URL

from cio.auth import get_token
from cio.config import config

API_URL = URL("https://api.clouding.io/v1")


class Method(StrEnum):
    # https://github.com/python/cpython/issues/115509#issuecomment-1946971056
    @staticmethod
    def _generate_next_value_(name, *args):
        return name.upper()

    GET = auto()
    PUT = auto()


class HeaderField(StrEnum):
    RATE_LIMIT_LIMIT = "X-Rate-Limit-Limit"
    RATE_LIMIT_REMAINING = "X-Rate-Limit-Remaining"
    RATE_LIMIT_RESET = "X-Rate-Limit-Reset"


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
        self.api_auth = {"X-API-KEY": get_token()}
        self._response = requests.Response()
        self.response = {}

    def print(self):
        print(json.dumps(self.response, indent=4, sort_keys=True))

    @property
    def _verbose(self):
        if "verbose" not in self.response:
            self.response["verbose"] = {}
        return self.response["verbose"]

    def request(self, method: Method, endpoint: str, headers: dict):
        headers.update(self.api_auth)
        self._response = requests.request(
            method, self.api_url / endpoint, headers=headers
        )
        if config.be_verbose:
            self._verbose.update(
                {"endpoint": endpoint, "status_code": self._response.status_code}
            )

        if self._response.status_code in ValidStatusCodes:
            if config.be_verbose:
                self._verbose.update(
                    {
                        HeaderField.RATE_LIMIT_REMAINING: self._response.headers[
                            HeaderField.RATE_LIMIT_REMAINING
                        ]
                    }
                )
        else:
            print("invalid HTTP status", self._response.status_code)
            exit(1)

    def get(self, endpoint: str, headers: dict = {}):
        self.request(Method.GET, endpoint, headers=headers)

    def put(self, endpoint: str, headers: dict = {}):
        self.request(Method.PUT, endpoint, headers=headers)
