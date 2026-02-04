import json

from pydantic import BaseModel, ValidationError

from cio.clouding import Clouding, DeleteResponse
from cio.config import config
from cio.resource import Resource


class RequestPayload(BaseModel):
    pass


class Endpoint[T: Resource]:
    def __init__(self, component_type: T, endpoint: str):
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

    def to_str(self, models: list[BaseModel] | BaseModel | None = None) -> str:
        list_name = self.endpoint
        if models is None:
            models = self.get()
        elif not isinstance(models, list):
            if isinstance(models, DeleteResponse):
                list_name = "delete"
            models = [models]
        result = {list_name: [model.model_dump() for model in models]}
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
    def _by_id(self) -> dict[str, T]:
        return {component.id: component for component in self.get()}

    @property
    def _by_name(self) -> dict[str, T]:
        return {component.name: component for component in self.get()}
