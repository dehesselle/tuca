from enum import StrEnum

from cio.component import Component, Components


class Server(Component):
    status: str
    publicIp: str


class Status(StrEnum):
    CREATING = "Creating"
    ACTIVE = "Active"


class Servers(Components):
    def __init__(self):
        super().__init__(Server, "servers")

    def create_from_snapshot(
        self,
        name: str,
        snapshot: str,
        flavor_id: str,
        password: str,
        wait_until_active: bool = False,
    ) -> None:
        payload = {
            "name": name,
            "hostname": name,  # TODO: sluggify?
            "flavorId": flavor_id,
            "accessConfiguration": {
                "sshKeyId": None,
                "password": password,
                "savePassword": True,
            },
            "volume": {
                "source": "snapshot",
                "id": snapshot,
                "ssdGb": 50,
            },  # TODO: configure size or get from snapshot
            "publicPortFirewallIds": ["verYGK55qgKakPLw"],  # TODO: obviously, get that
        }
        import json

        print(json.dumps(payload))
        # todo: when request bad, the error is not printed because its not in the response
        self._response = self.post(
            "servers", payload, headers={"Content-Type": "application/json"}
        )
        if self.is_ok:
            self.response = self._response.json()
        self.print()
