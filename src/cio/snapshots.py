from enum import StrEnum

from cio.clouding import Clouding


class Field(StrEnum):
    ID = "id"
    NAME = "name"
    CREATED_AT = "createdAt"


class Snapshots(Clouding):
    def list(self, id: str = ""):
        if id:
            self.get(f"snapshots/{id}")
            snapshots = [self._response.json()]
        else:
            self.get("snapshots")
            snapshots = self._response.json()["snapshots"]

        self.response["snapshots"] = []
        if self.is_ok:
            for snapshot in snapshots:
                self.response["snapshots"].append(
                    {key: snapshot[key] for key in [_.value for _ in Field]}
                )
        self.print()
