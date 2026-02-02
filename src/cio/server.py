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


def list_server(args):
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
        payload = CreateServerPayload(
            name=args.name,
            hostname=args.name,
            flavorId=args.flavorid,
            accessConfiguration=AccessConfiguration(
                sshKeyId=None, password=args.password, savePassword=True
            ),
            volume=Volume(
                source="snapshot", id=args.snapshot, ssdGb=50
            ),  # TODO: default size from snapshot
            publicPortFirewallIds=[firewall_id],
        )
        servers = Servers()
        server = servers.create(payload)
        print(servers.to_str(server))
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
