from enum import StrEnum

from cio.clouding import Clouding


class Field(StrEnum):
    ID = "id"
    NAME = "name"
    CREATED_AT = "createdAt"
    STATUS = "status"
    PUBLIC_IP = "publicIp"


class Status(StrEnum):
    CREATING = "Creating"
    ACTIVE = "Active"


class Servers(Clouding):
    def list(self, id: str = ""):
        if id:
            self.get(f"servers/{id}")
            servers = [self._response.json()]
        else:
            self.get("servers")
            servers = self._response.json()["servers"]

        self.response["servers"] = []
        if self.is_ok:
            for server in servers:
                self.response["servers"].append(
                    {key: server[key] for key in [_.value for _ in Field]}
                )
        self.print()
