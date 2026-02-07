# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import json
from typing import Type, cast

from pydantic import BaseModel, ValidationError

from tuca.clouding import Clouding, DeleteResponse
from tuca.config import config
from tuca.resource import IdentifiableResource, NamedResource, Resource


class RequestPayload(BaseModel):
    pass


class Endpoint[T: Resource]:
    def __init__(self, component_type: Type[T], endpoint: str):
        self.clouding = Clouding()
        self.resources: list[T] = []
        self.component_type = component_type
        self.endpoint = endpoint
        self.response_key = endpoint

    def create(self, payload: RequestPayload) -> list[T]:
        self.clouding.post(
            self.endpoint,
            payload.model_dump(),
            headers={"Content-Type": "application/json"},
        )
        return self._deserialize_response()

    def delete(self, id: str) -> DeleteResponse:
        self.clouding.delete(self.endpoint, id)
        return self.clouding.delete_response

    def get(self) -> list[T]:
        if not self.resources:
            self.clouding.get(self.endpoint)
            self.resources.extend(self._deserialize_response(self.response_key))
            while (
                len(self.resources) < 100 and self.clouding.next()
            ):  # TODO configurable limit?
                self.resources.extend(self._deserialize_response(self.response_key))
        return self.resources

    def get_by_id(self, id: str) -> T | None:
        try:
            return self._by_id[id]
        except KeyError:
            return None

    def get_by_name(self, name: str) -> T | None:
        try:
            return self._by_name[name]
        except KeyError:
            return None

    def to_str(self, resources: list[T] | T | None = None) -> str:
        if resources is None:
            resources = self.get()
        elif not isinstance(resources, list):
            resources = [resources]
        result = {self.endpoint: [resource.model_dump() for resource in resources]}
        return self._to_str(result)

    def list_resources(self, args: argparse.Namespace):
        if hasattr(args, "id") and args.id:
            print(self.to_str(self.get_by_id(args.id)))
        elif hasattr(args, "name") and args.name:
            print(self.to_str(self.get_by_name(args.name)))
        else:
            print(self.to_str())

    def delete_resource(self, args: argparse.Namespace):
        if args.name:
            if resource := self.get_by_name(args.name):
                resource_id = cast(NamedResource, resource).id
            else:
                resource_id = ""
        else:
            resource_id = args.id

        if resource_id:
            response = self.delete(resource_id)
            # TODO not checking anything
            print(self._to_str(response.to_dict()))
        else:
            print(f"resource_id not found: {resource_id}")  # TODO
            exit(1)

    def _to_str(self, response: dict) -> str:
        if config.be_verbose:
            response["verbose"] = {
                "endpoint": self.endpoint,
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

    def _deserialize_response(self, key: str = "") -> list[T]:
        self.resources.clear()
        if self.clouding.is_status_ok:
            try:
                self.resources.extend(
                    [
                        self.component_type.model_validate(_)
                        for _ in (
                            self.clouding.response.json()[key]
                            if key
                            else [self.clouding.response.json()]
                        )
                    ]
                )
            except KeyError:
                print("keyerror")  # TODO
            except ValidationError:
                print("validationerror")  # TODO
                print(self.clouding.response.json()[key])
        else:
            print(f"HTTP {self.clouding.response.status_code}")  # TODO
        return self.resources

    @property
    def _by_id(
        self,
    ) -> dict[str, T]:
        return {
            cast(IdentifiableResource, resource).id: resource for resource in self.get()
        }

    @property
    def _by_name(self) -> dict[str, T]:
        return {cast(NamedResource, resource).name: resource for resource in self.get()}
