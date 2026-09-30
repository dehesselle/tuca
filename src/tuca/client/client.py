# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import json
import logging
from http import HTTPStatus

import requests

from tuca.cost import Cost
from tuca.endpoints.actions import Actions
from tuca.endpoints.firewalls import Firewalls
from tuca.endpoints.flavors import Flavors
from tuca.endpoints.images import Images
from tuca.endpoints.keypairs import Keypairs
from tuca.endpoints.servers import Servers
from tuca.endpoints.snapshots import Snapshots
from tuca.endpoints.volumes import Volumes
from tuca.resources.action import Action

from .response import Pagination, ResponseHeader

log = logging.getLogger("client")


ValidStatusCodes = (
    HTTPStatus.ACCEPTED,
    HTTPStatus.BAD_REQUEST,
    HTTPStatus.CREATED,
    HTTPStatus.FORBIDDEN,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.METHOD_NOT_ALLOWED,
    HTTPStatus.NO_CONTENT,
    HTTPStatus.NOT_FOUND,
    HTTPStatus.OK,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.UNAUTHORIZED,
)  # https://api.clouding.io/docs/#section/Introduction/Responses


class Client:
    """entry point for using tuca as a library

    The client does the HTTP work itself; its endpoints call back into it.
    It wraps the basic operations from the requests package and adds some
    Clouding specifics (authentication, simple pagination).
    See the `introduction`_ section of the documentation.

    .. _introduction:
       https://api.clouding.io/docs/#section/Introduction
    """

    def __init__(self, token: str, timeout: int = 30):
        self.base_url = "https://api.clouding.io/v1"
        self.authentication = {"X-API-KEY": token}
        self.timeout = timeout  # seconds, per request
        self.resource = ""
        self.response = requests.Response()
        self.response_header = ResponseHeader()
        self.response_page_size = 100
        self.pagination = Pagination()
        self.actions = Actions(self)
        self.firewalls = Firewalls(self)
        self.flavors = Flavors(self)
        self.images = Images(self)
        self.keypairs = Keypairs(self)
        self.servers = Servers(self)
        self.snapshots = Snapshots(self)
        self.volumes = Volumes(self)
        self.cost = Cost(self)

    def get(self, resource: str):
        self.resource = resource
        self.response = requests.get(
            f"{self.base_url}/{resource}",
            params={"pageSize": self.response_page_size},
            headers=self.authentication,
            timeout=self.timeout,
        )
        self._process_response()

    def post(
        self, resource: str, payload: dict | None = None, headers: dict | None = None
    ):
        payload = payload or {}
        headers = headers or {}
        self.resource = resource
        headers.update(self.authentication)
        self.response = requests.post(
            f"{self.base_url}/{resource}",
            data=json.dumps(payload),
            headers=headers,
            timeout=self.timeout,
        )
        self._process_response()

    def delete(self, resource: str, id: str) -> Action | None:
        self.resource = resource
        self.response = requests.delete(
            f"{self.base_url}/{resource}/{id}",
            headers=self.authentication,
            timeout=self.timeout,
        )
        action = (
            Action.model_validate(self.response.json()) if self.has_content else None
        )
        self._process_response()
        return action

    def next(self) -> bool:
        if url := self.pagination.links.next:
            self.response = requests.get(
                url, headers=self.authentication, timeout=self.timeout
            )
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
            HTTPStatus.ACCEPTED,
            HTTPStatus.CREATED,
            HTTPStatus.NO_CONTENT,
            HTTPStatus.OK,
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
