# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import json
import logging
from http import HTTPStatus

import requests
from urlpath import URL

from tuca.resources.action import Action

from .auth import get_token
from .response import Pagination, ResponseHeader

log = logging.getLogger("clouding")


ValidStatusCodes = (
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
)  # https://api.clouding.io/docs/#section/Introduction/Responses


class Clouding:
    """low-level API wrapper

    This class wraps the basic operations from the requests package and adds some
    Clouding specifics (authentication, simple pagination).
    See the `introduction`_ section of the documentation.

    .. _introduction:
       https://api.clouding.io/docs/#section/Introduction
    """

    def __init__(self):
        self.base_url = URL("https://api.clouding.io/v1")
        self.authentication = {"X-API-KEY": get_token(None)}
        self.resource = URL("")
        self.response = requests.Response()
        self.response_header = ResponseHeader()
        self.response_page_size = 100
        self.pagination = Pagination()
        self.action: Action

    def get(self, resource: URL):
        self.resource = resource
        self.response = requests.get(
            str(self.base_url / resource / f"?pageSize={self.response_page_size}"),
            headers=self.authentication,
        )
        self._process_response()

    def post(self, resource: URL, payload: dict = {}, headers: dict = {}):
        self.resource = resource
        headers.update(self.authentication)
        self.response = requests.post(
            str(self.base_url / resource), data=json.dumps(payload), headers=headers
        )
        self._process_response()

    def delete(self, resource: URL, id: str):
        self.resource = resource
        self.response = requests.delete(
            str(self.base_url / resource / id), headers=self.authentication
        )
        if self.has_content:
            self.action = Action.model_validate(self.response.json())
        self._process_response()

    def next(self) -> bool:
        if url := self.pagination.links.next:
            self.response = requests.get(url, headers=self.authentication)
            self._process_response()
            return True
        else:
            return False

    @property
    def is_status_not_found(self) -> bool:
        return self.response.status_code == HTTPStatus.NOT_FOUND

    @property
    def is_status_ok(self) -> bool:
        return self.response.status_code in (
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.ACCEPTED,
            HTTPStatus.NO_CONTENT,
        )

    @property
    def is_status_valid(self) -> bool:
        return self.response.status_code in ValidStatusCodes

    @property
    def has_content(self) -> bool:
        return self.is_status_ok and self.response.status_code != HTTPStatus.NO_CONTENT

    def _process_response(self):
        if self.has_content:
            self.response_header = ResponseHeader.model_validate(self.response.headers)
            self.pagination = Pagination.model_validate(self.response.json())
