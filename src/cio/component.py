import json

from pydantic import BaseModel

from .clouding import Clouding
from .config import config


class Component(BaseModel):
    id: str
    name: str
    createdAt: str

    @property
    def as_str(self):
        return json.dumps(
            self.model_dump(),
            indent=4,
            sort_keys=True,
        )


class Components:
    def __init__[T: Component](self, component_type: T, endpoint: str):
        self.clouding = Clouding()
        self._all = []
        self.component_type = component_type
        self.endpoint = endpoint

    @property
    def all[T: Component](self) -> list[T]:
        if not self._all:
            self.clouding.get(self.endpoint)
            if self.clouding.is_status_ok:
                self._all.extend(
                    [
                        self.component_type.model_validate(_)
                        for _ in self.clouding.response.json()[self.endpoint]
                    ]
                )

        return self._all

    def _to_str(self, components: list[Component]) -> str:
        result = {self.endpoint: [component.model_dump() for component in components]}
        if config.be_verbose:
            result["verbose"] = {
                "endpoint": self.endpoint,
                "status_code": self.clouding.response.status_code,
            }
            result["verbose"].update(self.clouding.header.model_dump())

        return json.dumps(
            result,
            indent=4,
            sort_keys=True,
        )

    @property
    def all_as_str(self) -> str:
        return self._to_str(self.all)

    @property
    def all_by_id[T: Component](self) -> dict[str, T]:
        return {component.id: component for component in self.all}

    @property
    def all_by_name[T: Component](self) -> dict[str, T]:
        return {component.name: component for component in self.all}

    def one_as_str(self, component_id: str) -> str:
        try:
            return self._to_str([self.all_by_id[component_id]])
        except KeyError:
            return ""
