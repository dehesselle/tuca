import json
from typing import Self

from pydantic import BaseModel, ValidationError

from .clouding import Clouding
from .config import config


class Component(BaseModel):
    id: str
    name: str

    @property
    def as_str(self):
        return json.dumps(
            self.model_dump(),
            indent=4,
            sort_keys=True,
        )


class CreatePayload(BaseModel):
    pass


class Components[T: Component]:
    def __init__(self, component_type: T, endpoint: str):
        self.clouding = Clouding()
        self._all = []
        self.component_type = component_type
        self.endpoint = endpoint
        self.response_key = endpoint

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
        else:
            print("server response error")  # TODO
        return result

    @property
    def all(self) -> list[T]:
        if not self._all:
            self.clouding.get(self.endpoint)
            self._all.extend(self._deserialize_response(self.response_key))
        return self._all

    def to_str(self, components: list[T] | T) -> str:
        if not isinstance(components, list):
            components = [components]
        result = {self.endpoint: [component.model_dump() for component in components]}
        if config.be_verbose:
            result["verbose"] = {
                "endpoint": self.endpoint,
                "status_code": self.clouding.response.status_code,
            }
            result["verbose"].update(self.clouding.response_header.model_dump())

        return json.dumps(
            result,
            indent=4,
            sort_keys=True,
        )

    @property
    def all_as_str(self) -> str:
        return self.to_str(self.all)

    @property
    def all_by_id(self) -> dict[str, T]:
        return {component.id: component for component in self.all}

    @property
    def all_by_name(self) -> dict[str, T]:
        return {component.name: component for component in self.all}

    def get_by_id(self, id: str) -> T | None:
        try:
            return self.all_by_id[id]
        except KeyError:
            return None

    def get_by_name(self, name: str) -> T | None:
        try:
            return self.all_by_name[name]
        except KeyError:
            return None

    def set_endpoint(self, endpoint: str) -> Self:
        self.endpoint = endpoint
        return self

    def create(self, payload: CreatePayload) -> list[T]:
        self.clouding.post(
            self.endpoint,
            payload.model_dump(),
            headers={"Content-Type": "application/json"},
        )
        return self._deserialize_response()

    def delete(self, id: str):
        self.clouding.delete(self.endpoint + f"/{id}")
