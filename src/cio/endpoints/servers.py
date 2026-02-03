from argparse import _SubParsersAction
from enum import StrEnum, auto

from pydantic import BaseModel

from cio.resource import Resource

from .endpoint import Endpoint, RequestPayload
from .firewalls import Firewalls
from .sizes import Flavors


class Action(StrEnum):
    LIST = auto()
    CREATE = auto()
    DELETE = auto()


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


class CreateRequestPayload(RequestPayload):
    name: str
    hostname: str
    flavorId: str
    accessConfiguration: AccessConfiguration
    volume: Volume
    publicPortFirewallIds: list[str]


class Server(Resource):
    id: str
    name: str
    createdAt: str = ""
    publicIp: str | None = ""
    status: str


class Servers(Endpoint[Server]):
    def __init__(self):
        super().__init__(Server, "servers")


def create_server(args):
    if args.flavorid not in Flavors().all:
        print(f"flavor not supported: {args.flavorid}")
        exit(1)

    firewall_id = 0
    if firewall := Firewalls().get_by_name(args.firewall):
        firewall_id = firewall.id
    if firewall_id:
        payload = CreateRequestPayload(
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
            server_id = ""
    else:
        server_id = args.id

    if server_id:
        response = servers.delete(server_id)
        # TODO not checking anything
        print(servers.to_str(response))
    else:
        print("not found - no delete")  # TODO
        exit(1)


def list_server(args):
    servers = Servers()
    if args.id:
        print(servers.to_str(servers.get_by_id(args.id)))
    else:
        print(servers.to_str())


def setup_servers_endpoint(subparser: _SubParsersAction):
    servers = subparser.add_parser("servers", help="manage servers")
    server_actions = servers.add_subparsers(help="available actions")

    server_action_create = server_actions.add_parser(
        Action.CREATE, help="create new server"
    )
    server_action_create.add_argument("--name", type=str, required=True)
    server_action_create.add_argument("--snapshot", type=str, required=True)
    server_action_create.add_argument("--flavorid", type=str, required=True)
    server_action_create.add_argument(
        "--firewall", type=str, required=False, default="default"
    )
    server_action_create.add_argument("--password", type=str, required=True)
    server_action_create.set_defaults(func=create_server)

    server_action_delete = server_actions.add_parser(
        Action.DELETE, help="delete a server"
    )
    id_or_name = server_action_delete.add_mutually_exclusive_group(required=True)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    server_action_delete.set_defaults(func=delete_server)

    server_action_list = server_actions.add_parser(Action.LIST, help="list servers")
    server_action_list.add_argument("-i", "--id", type=str, default="", required=False)
    server_action_list.set_defaults(func=list_server)
