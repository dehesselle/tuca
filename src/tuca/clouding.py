# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import json
from http import HTTPStatus

import requests
from pydantic import BaseModel, Field
from urlpath import URL

from tuca.auth import get_token


class ResponseHeader(BaseModel):
    rate_limit_limit: str = Field(alias="X-Rate-Limit-Limit", default="")
    rate_limit_remaining: str = Field(alias="X-Rate-Limit-Remaining", default="")
    rate_limit_reset: str = Field(alias="X-Rate-Limit-Reset", default="")


class DeleteResponse(BaseModel):
    id: str
    status: str = ""
    startedAt: str = ""
    resourceId: str = ""
    resourceType: str = ""

    def to_dict(self) -> dict:
        return {"delete": [self.model_dump()]}


class ResponseLinks(BaseModel):
    next: str | None
    previous: str | None


class ResponseMeta(BaseModel):
    total: int


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
        self.query = ""
        self.response = requests.Response()
        self.response_header = ResponseHeader()
        self.response_links = ResponseLinks(next=None, previous=None)
        self.response_meta = ResponseMeta(total=0)
        self.delete_response = DeleteResponse(id="")

    def get(self, endpoint: str):
        self.endpoint = endpoint
        self.response = requests.get(
            str(self.api_url / endpoint / "?pageSize=100"), headers=self.api_auth
        )
        self._post_processing()

    def post(self, endpoint: str, payload: dict, headers: dict = {}):
        self.endpoint = endpoint
        headers.update(self.api_auth)
        self.response = requests.post(
            str(self.api_url / endpoint), data=json.dumps(payload), headers=headers
        )
        self._post_processing()

    def delete(self, endpoint: str, id: str):
        self.endpoint = endpoint
        self.response = requests.delete(
            str(self.api_url / endpoint / id), headers=self.api_auth
        )
        if self.has_content:
            self.delete_response = DeleteResponse.model_validate(self.response.json())
        else:
            self.delete_response.resourceId = id  # the only piece of info we got
        self._post_processing()

    def next(self) -> bool:
        if url := self.response_links.next:
            print(self.response_links.next)
            self.response = requests.get(url, headers=self.api_auth)
            self._post_processing()
            return True
        else:
            return False

    @property
    def is_status_ok(self) -> bool:
        return self.response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.ACCEPTED,
            HTTPStatus.NO_CONTENT,
        ]

    @property
    def is_status_valid(self) -> bool:
        return self.response.status_code in ValidStatusCodes

    @property
    def has_content(self) -> bool:
        return self.is_status_ok and self.response.status_code != HTTPStatus.NO_CONTENT

    def _post_processing(self):
        if self.is_status_valid:
            self.response_header = ResponseHeader.model_validate(self.response.headers)
            try:
                self.response_links = ResponseLinks.model_validate(
                    self.response.json()["links"]
                )
                self.response_meta = ResponseMeta.model_validate(
                    self.response.json()["meta"]
                )
            except KeyError:
                pass  # non-paginated responses don't have links and meta
        else:
            # FIXME: rework error handling
            print("invalid HTTP status", self.response.status_code)
            exit(1)
