# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import json
from typing import Type

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

    def delete(self: "Endpoint[IdentifiableResource]", id: str) -> DeleteResponse:
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

    def get_by_id(
        self: "Endpoint[IdentifiableResource]", id: str
    ) -> IdentifiableResource | None:
        try:
            return self._by_id[id]
        except KeyError:
            return None

    def get_by_name(self: "Endpoint[NamedResource]", name: str) -> NamedResource | None:
        try:
            return self._by_name[name]
        except KeyError:
            return None

    def to_str(self, models: list[T] | T | None = None) -> str:
        list_name = self.endpoint
        if models is None:
            models = self.get()
        elif not isinstance(models, list):
            if isinstance(models, DeleteResponse):
                list_name = "delete"
            models = [models]
        result = {list_name: [model.model_dump() for model in models]}
        if config.be_verbose:
            result["verbose"] = {  # pyright: ignore[reportArgumentType]
                "endpoint": self.endpoint,
                "status_code": self.clouding.response.status_code,
            }
            result["verbose"].update(self.clouding.response_header.model_dump())
        return json.dumps(
            result,
            indent=4,
            sort_keys=True,
        )

    @classmethod
    def list_resources(
        cls, args: argparse.Namespace
    ):  # This is like an abstract method *but* with a body, i.e. the code
        # here works for derived classes but doesn't work for the base class.
        # That's what PyLance complains about.
        # I haven't come up with a better solution yet.
        endpoint = cls()
        if hasattr(args, "id") and args.id:
            print(endpoint.to_str(endpoint.get_by_id(args.id)))
        elif hasattr(args, "name") and args.name:
            print(endpoint.to_str(endpoint.get_by_name(args.name)))
        else:
            print(endpoint.to_str())

    @classmethod
    def delete_resource(
        cls, args: argparse.Namespace
    ):  # See comment in list_resources() above.
        endpoint = cls()
        if args.name:
            if resource := endpoint.get_by_name(args.name):
                resource_id = resource.id
            else:
                resource_id = ""
        else:
            resource_id = args.id

        if resource_id:
            response = endpoint.delete(resource_id)
            # TODO not checking anything
            print(endpoint.to_str(response))
        else:
            print(f"resource_id not found: {resource_id}")  # TODO
            exit(1)

    def _deserialize_response(self, key: str = "") -> list[T]:
        result = []
        if self.clouding.is_status_ok:
            try:
                result.extend(
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
        return result

    @property
    def _by_id(
        self: "Endpoint[IdentifiableResource]",
    ) -> dict[str, IdentifiableResource]:
        return {resource.id: resource for resource in self.get()}

    @property
    def _by_name(self: "Endpoint[NamedResource]") -> dict[str, NamedResource]:
        return {resource.name: resource for resource in self.get()}
