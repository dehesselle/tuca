# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import json
import logging
from typing import Type, cast

from pydantic import BaseModel, ValidationError
from urlpath import URL

from tuca.clouding import Action, Clouding

from .resource import IdentifiableResource, NamedResource, Resource

log = logging.getLogger("endpoint")


class RequestPayload(BaseModel):
    pass


class Endpoint[T: Resource]:
    """base class for all endpoints"""

    be_verbose: bool = False

    def __init__(self, resource_type: Type[T], endpoint: str):
        self.clouding = Clouding()
        self.resources: list[T] = []
        self.resource_type = resource_type
        self.endpoint = URL(endpoint)
        self.response_key = endpoint

    def create(self, payload: RequestPayload) -> list[T]:
        self.resources.clear()
        self.clouding.post(
            self.endpoint,
            payload.model_dump(),
            headers={"Content-Type": "application/json"},
        )
        self.resources.extend(self._deserialize_resources())
        return self.resources

    def delete(self, id: str) -> Action:
        self.resources.clear()
        self.clouding.delete(self.endpoint, id)
        return self.clouding.action

    def get(self) -> list[T]:
        self.resources.clear()
        self.clouding.get(self.endpoint)
        self.resources.extend(self._deserialize_resources(self.response_key))
        while self.clouding.next():  # pagination
            self.resources.extend(self._deserialize_resources(self.response_key))
        return self.resources

    def get_by_id(self, id: str) -> T | None:
        self.resources.clear()
        self.clouding.get(self.endpoint / id)
        self.resources.extend(self._deserialize_resources())
        return self.resources[0] if self.resources else None

    def get_by_name(self, name: str) -> T | None:
        try:
            return self._by_name[name]
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

    def to_str(self, resources: list[T] | T | None = None) -> str:
        if resources is None:
            resources = self.get()
        elif not isinstance(resources, list):
            resources = [resources]
        result = {str(self.endpoint): [resource.model_dump() for resource in resources]}
        return self._to_str(result)

    def delete_resource(self, args: argparse.Namespace):
        if args.name:
            if resource := self.get_by_name(args.name):
                resource_id = cast(NamedResource, resource).id
            else:
                resource_id = ""
        else:
            resource_id = args.id

        if resource_id:
            action = self.delete(resource_id)
            if action.id:  # not every delete request produces an action
                print(self._to_str(action.as_dict))
        else:
            if args.name:
                log.error(f"resource name not found: {args.name}")
                exit(1)
            else:
                log.error(f"resource id not found: {resource_id}")
                exit(1)

    def list_resources(self, args: argparse.Namespace):
        if hasattr(args, "id") and args.id:
            print(self.to_str(self.get_by_id(args.id)))
        elif hasattr(args, "name") and args.name:
            print(self.to_str(self.get_by_name(args.name)))
        elif hasattr(args, "filter") and args.filter:
            print(self.to_str(self.find(args.filter)))
        else:
            print(self.to_str())

    def _to_str(self, response: dict) -> str:
        if self.be_verbose:
            response["verbose"] = {
                "endpoint": str(self.endpoint),
                "status_code": self.clouding.response.status_code,
            }
            response["verbose"].update(
                self.clouding.response_header.model_dump(
                    include={"rate_limit_remaining"}
                )
            )
        return json.dumps(
            response,
            indent=4,
            sort_keys=True,
        )

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
                log.error(f"response.json lacks key: {key}")
                log.error(self.clouding.response.json())
                exit(1)
            except ValidationError:
                log.error(f"unable to deserialize contents of: {key}")
                exit(1)
        elif self.clouding.is_status_not_found:
            log.error("resource(s) not found")
            exit(1)
        else:
            log.error(f"HTTP status: {self.clouding.response.status_code}")
            exit(1)
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
                log.error(f"response.json lacks action")
                log.error(self.clouding.response.json())
                exit(1)
            except ValidationError:
                log.error(f"unable to deserialize contents of action")
                exit(1)
        elif self.clouding.is_status_not_found:
            log.error("resource not found")
            exit(1)
        else:
            log.error(f"HTTP status: {self.clouding.response.status_code}")
            exit(1)
        return self.action

    @property
    def _by_id(
        self,
    ) -> dict[str, T]:
        if not self.resources:
            self.get()
        return {
            cast(IdentifiableResource, resource).id: resource
            for resource in self.resources
        }

    @property
    def _by_name(self) -> dict[str, T]:
        if not self.resources:
            self.get()
        return {
            cast(NamedResource, resource).name: resource for resource in self.resources
        }
