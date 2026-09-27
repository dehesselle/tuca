# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from pydantic import BaseModel, ValidationError

from tuca.resources.action import Action
from tuca.resources.resource import (
    IdentifiableResource,
    NamedResource,
    Resource,
)

if TYPE_CHECKING:
    from tuca.client import Client

log = logging.getLogger("endpoint")


class EndpointError(Exception):
    pass


class ResourceNotFoundError(EndpointError):
    pass


class DeserializationError(EndpointError):
    def __init__(self, message, response):
        super().__init__(message, response)

    def __str__(self):
        return f"{self.args[0]}\nresponse:\n{self.args[1]}"


class HttpError(EndpointError):
    pass


class Endpoint[T: Resource]:
    """base class for all endpoints"""

    def __init__(self, resource_type: type[T], resource: str, client: Client):
        self.client = client
        self.resources: list[T] = []
        self.resource_type = resource_type
        self.resource = resource
        self.response_key = resource

    def _create(self, payload: BaseModel) -> list[T]:
        self.resources.clear()
        self.client.post(
            self.resource,
            payload.model_dump(),
            headers={"Content-Type": "application/json"},
        )
        self.resources.extend(self._deserialize_resources())
        return self.resources

    def delete(self, id: str) -> Action | None:
        self.resources.clear()
        self.client.delete(self.resource, id)
        return self.client.action

    def delete_by_name(self, name: str) -> Action | None:
        if resource := self.get_one_by_name(name):
            return self.delete(cast(NamedResource, resource).id)
        else:
            raise ResourceNotFoundError(f"resource name not found: {name}")

    # naming convention: How to properly name "get one resource" vs.
    # "get all resources" methods? I've decided to follow Textual's example
    # with its query() and query_one() methods.

    def get(self) -> list[T]:
        self.resources.clear()
        self.client.get(self.resource)
        self.resources.extend(self._deserialize_resources(self.response_key))
        while self.client.next():  # pagination
            self.resources.extend(self._deserialize_resources(self.response_key))
        return self.resources

    def get_one(self, id: str) -> T | None:
        self.resources.clear()
        self.client.get(f"{self.resource}/{id}")
        self.resources.extend(self._deserialize_resources())
        try:
            return self.resources[0]
        except IndexError:
            log.debug(f"resource id not found: {id}")
            return None

    def get_one_by_name(self, name: str) -> T | None:
        # The API does not support requesting a single resource
        # by name, so we have to request them all and then
        # select the one we want.
        try:
            return self.by_name[name]
        except KeyError:
            return None

    def find(self, filter: str) -> list[T]:
        if not self.resources:
            self.get()
        return [
            resource
            for resource in self.resources
            if (
                hasattr(resource, "id")
                and filter.lower() in cast(IdentifiableResource, resource).id.lower()
            )
            or (
                hasattr(resource, "name")
                and filter.lower() in cast(NamedResource, resource).name.lower()
            )
        ]

    def _deserialize_resources(self, key: str = "") -> list[T]:
        result = []
        if self.client.is_status_ok:
            try:
                result.extend(
                    [
                        self.resource_type.model_validate(_)
                        for _ in (
                            self.client.response.json()[key]
                            if key
                            else [self.client.response.json()]
                        )
                    ]
                )
            except KeyError:
                raise DeserializationError(
                    f"response.json lacks key: {key}", self.client.response.json()
                )
            except ValidationError:
                raise DeserializationError(
                    f"unable to deserialize contents of: {key}",
                    self.client.response.json(),
                )
        elif self.client.is_status_not_found:
            # not a breaking error here, needs to be handled upstream
            log.debug("resource(s) not found")
        else:
            raise HttpError(f"HTTP status: {self.client.response.status_code}")
        return result

    def _deserialize_action(self, key: str = "") -> Action:
        if self.client.is_status_ok:
            try:
                self.action = Action.model_validate(
                    self.client.response.json()[key]
                    if key
                    else self.client.response.json()
                )
            except KeyError:
                raise DeserializationError(
                    "response.json lacks action", self.client.response.json()
                )
            except ValidationError:
                raise DeserializationError(
                    "unable to deserialize contents of action",
                    self.client.response.json(),
                )
        elif self.client.is_status_not_found:
            raise ResourceNotFoundError("resource not found")
        else:
            raise HttpError(f"HTTP status: {self.client.response.status_code}")
        return self.action

    @property
    def by_id(
        self,
    ) -> dict[str, T]:
        if not self.resources:
            self.get()
        return {
            cast(IdentifiableResource, resource).id: resource
            for resource in self.resources
        }

    @property
    def by_name(self) -> dict[str, T]:
        if not self.resources:
            self.get()
        return {
            cast(NamedResource, resource).name: resource for resource in self.resources
        }
