from enum import StrEnum
from typing import Optional

from pydantic import BaseModel

from cio.component import Component, Components
from cio.firewall import Firewalls


class Server(Component):
    createdAt: Optional[str] = ""
    publicIp: Optional[str] = ""
    status: str


class Status(StrEnum):
    CREATING = "Creating"
    ACTIVE = "Active"
    PENDING = "Pending"


class AccessConfiguration(BaseModel):
    sshKeyId: str | None
    password: str
    savePassword: bool


class Volume(BaseModel):
    source: str
    id: str
    ssdGb: int


class CreateServerPayload(BaseModel):
    name: str
    hostname: str
    flavorId: str
    accessConfiguration: AccessConfiguration
    volume: Volume
    publicPortFirewallIds: list


class Servers(Components):
    def __init__(self):
        super().__init__(Server, "servers")

    def create_from_snapshot(
        self,
        name: str,
        snapshot: str,
        flavor_id: str,
        password: str,
        firewall: str,
        wait_until_active: bool = False,
    ) -> str:
        payload = CreateServerPayload(
            name=name,
            hostname=name,
            flavorId=flavor_id,
            accessConfiguration=AccessConfiguration(
                sshKeyId=None, password=password, savePassword=True
            ),
            volume=Volume(
                source="snapshot", id=snapshot, ssdGb=50
            ),  # TODO: default size from snapshot
            publicPortFirewallIds=[firewall],
        )

        return self.to_str(self.create(payload))

        # # TODO: when request bad, the error is not printed because its not in the response
        # self.clouding.post(
        #     "servers",
        #     payload.model_dump(),
        #     headers={"Content-Type": "application/json"},
        # )
        # print(self.clouding.response.json())
        # print("---------------")
        # print(self.clouding.response.text)


def list_servers(args):
    servers = Servers()
    if args.id:
        try:
            print(servers.all_by_id[args.id].as_str)
        except KeyError:
            exit(1)
    else:
        print(servers.all_as_str)


def create_server(args):
    firewall_id = 0
    if firewall := Firewalls().get_by_name(args.firewall):
        firewall_id = firewall.id
    if firewall_id:
        servers = Servers()
        result_str = servers.create_from_snapshot(
            args.name, args.snapshot, args.flavorid, args.password, firewall_id
        )
        print(result_str)
    else:
        print("error no firewall_id")  # TODO
        exit(1)


def delete_server(args):
    servers = Servers()
    if args.name:
        if server := servers.get_by_name(args.name):
            server_id = server.id
        else:
            server_id = 0
    else:
        server_id = args.id

    if server_id:
        servers.delete(server_id)
        print("after delete")
        print(servers.clouding.response.json())
    else:
        print("not found - no delete")  # TODO
        exit(1)
