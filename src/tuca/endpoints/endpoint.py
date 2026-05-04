# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import json
import logging
from typing import Type, cast

from pydantic import BaseModel, ValidationError
from urlpath import URL

from tuca.clouding import Clouding
from tuca.resources.action import Action
from tuca.resources.resource import (
    IdentifiableResource,
    NamedResource,
    Resource,
)

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

    be_verbose: bool = False

    def __init__(self, resource_type: Type[T], resource: str):
        self.clouding = Clouding()
        self.resources: list[T] = []
        self.resource_type = resource_type
        self.resource = URL(resource)
        self.response_key = resource

    def _create(self, payload: BaseModel) -> list[T]:
        self.resources.clear()
        self.clouding.post(
            self.resource,
            payload.model_dump(),
            headers={"Content-Type": "application/json"},
        )
        self.resources.extend(self._deserialize_resources())
        return self.resources

    def delete(self, id: str) -> Action | None:
        self.resources.clear()
        self.clouding.delete(self.resource, id)
        return self.clouding.action

    def delete_by_name(self, name: str):
        if resource := self.get_one_by_name(name):
            resource_id = cast(NamedResource, resource).id

            if action := self.delete(
                resource_id
            ):  # not every delete request produces an action
                print(self._to_str({"actions": [action.to_dict(self.be_verbose)]}))
        else:
            raise ResourceNotFoundError(f"resource name not found: {name}")

    # naming convention: How to properly name "get one resource" vs.
    # "get all resources" methods? I've decided to follow Textual's example
    # with its query() and query_one() methods.

    def get(self) -> list[T]:
        self.resources.clear()
        self.clouding.get(self.resource)
        self.resources.extend(self._deserialize_resources(self.response_key))
        while self.clouding.next():  # pagination
            self.resources.extend(self._deserialize_resources(self.response_key))
        return self.resources

    def get_one(self, id: str) -> T | None:
        self.resources.clear()
        self.clouding.get(self.resource / id)
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

    def _to_str(self, resources: dict) -> str:
        if self.be_verbose:
            resources["header"] = {  # pyright: ignore[reportArgumentType]
                "status_code": self.clouding.response.status_code,
            }
            resources["header"].update(self.clouding.response_header.model_dump())

        return json.dumps(
            resources,
            indent=4,
            sort_keys=True,
        )

    def to_str(self) -> str:
        resources = {
            str(self.resource): [
                resource.to_dict(self.be_verbose) for resource in self.resources
            ]
        }
        return self._to_str(resources)

    def _deserialize_resources(self, key: str = "") -> list[T]:
        result = []
        if self.clouding.is_status_ok:
            try:
                result.extend(
                    [
                        self.resource_type.model_validate(_)
                        for _ in (
                            self.clouding.response.json()[key]
                            if key
                            else [self.clouding.response.json()]
                        )
                    ]
                )
            except KeyError:
                raise DeserializationError(
                    f"response.json lacks key: {key}", self.clouding.response.json()
                )
            except ValidationError:
                raise DeserializationError(
                    f"unable to deserialize contents of: {key}",
                    self.clouding.response.json(),
                )
        elif self.clouding.is_status_not_found:
            # not a breaking error here, needs to be handled upstream
            log.debug("resource(s) not found")
        else:
            raise HttpError(f"HTTP status: {self.clouding.response.status_code}")
        return result

    def _deserialize_action(self, key: str = "") -> Action:
        if self.clouding.is_status_ok:
            try:
                self.action = Action.model_validate(
                    self.clouding.response.json()[key]
                    if key
                    else self.clouding.response.json()
                )
            except KeyError:
                raise DeserializationError(
                    "response.json lacks action", self.clouding.response.json()
                )
            except ValidationError:
                raise DeserializationError(
                    "unable to deserialize contents of action",
                    self.clouding.response.json(),
                )
        elif self.clouding.is_status_not_found:
            raise ResourceNotFoundError("resource not found")
        else:
            raise HttpError(f"HTTP status: {self.clouding.response.status_code}")
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


def list_resources(endpoint: Endpoint, args: argparse.Namespace):
    if hasattr(args, "id") and args.id:
        if endpoint.get_one(args.id):
            print(endpoint.to_str())
        else:
            print(endpoint.to_str())
    elif hasattr(args, "name") and args.name:
        if endpoint.get_one_by_name(args.name):
            print(endpoint.to_str())
        else:
            print(endpoint.to_str())
    elif hasattr(args, "filter") and args.filter:
        endpoint.find(args.filter)
        print(endpoint.to_str())
    else:
        endpoint.get()
        print(endpoint.to_str())
