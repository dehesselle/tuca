# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import platform
import signal
import time
from argparse import _SubParsersAction
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from enum import StrEnum, auto

from pydantic import BaseModel
from slugify import slugify

from tuca.resource import NamedResource

from .endpoint import Endpoint, RequestPayload
from .firewalls import Firewalls
from .images import Images
from .sizes import Flavors
from .snapshots import Snapshots


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
    password: str | None
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


class Server(NamedResource):
    createdAt: str = ""
    publicIp: str | None = ""
    status: str


class Servers(Endpoint[Server]):
    def __init__(self):
        super().__init__(Server, "servers")

    @classmethod
    def create_resource(cls, args):
        if args.flavorid not in Flavors().all:
            print(f"flavor not supported: {args.flavorid}")
            exit(1)

        if args.snapshot:
            if snapshot := Snapshots().get_by_id(args.snapshot):
                volume = Volume(
                    source="snapshot", id=args.snapshot, ssdGb=snapshot.sizeGb
                )
            else:
                print(f"snapshot not found: {args.snapshot}")
                exit(1)
        elif args.image:
            if image := Images().get_by_id(args.image):
                volume = Volume(
                    source="image", id=args.image, ssdGb=image.minimumSizeGb
                )
            else:
                print(f"image not found: {args.image}")
                exit(1)
        else:
            print("mandatory mutually exclusive option missing")
            exit(1)

        if args.password:
            access_configuration = AccessConfiguration(
                sshKeyId=None, password=args.password, savePassword=True
            )
        elif args.sshkey:
            access_configuration = AccessConfiguration(
                sshKeyId=args.sshkey, password=None, savePassword=False
            )
        else:
            print("mandatory mutually exclusive option missing")
            exit(1)

        firewall_id = 0
        if firewall := Firewalls().get_by_name(args.firewall):
            firewall_id = firewall.id
        if firewall_id:
            payload = CreateRequestPayload(
                name=args.name,
                hostname=slugify(args.name),
                flavorId=args.flavorid,
                accessConfiguration=access_configuration,
                volume=volume,
                publicPortFirewallIds=[firewall_id],
            )
            servers = Servers()
            if server := servers.create(payload):
                server_id = server[0].id
                if args.wait:
                    if platform.system() == "Windows":
                        signal.signal(signal.SIGINT, signal.SIG_DFL)  # make ctrl+c work
                    with ThreadPoolExecutor() as executor:

                        def wait(id: str, status: Status, seconds: int) -> None:
                            while server := Servers().get_by_id(id):
                                if server.status == status:
                                    break
                                time.sleep(seconds)

                        future = executor.submit(wait, server_id, Status.ACTIVE, 30)
                        try:
                            future.result(timeout=300)
                        except TimeoutError:
                            future.cancel()
                print(servers.to_str(Servers().get_by_id(server_id)))
            else:
                print("failed to create server")
        else:
            print("error no firewall_id")  # TODO
            exit(1)


def setup_servers_endpoint(subparser: _SubParsersAction):
    servers = subparser.add_parser("servers", help="manage servers")
    server_actions = servers.add_subparsers(help="available actions")

    server_action_create = server_actions.add_parser(
        Action.CREATE, help="create new server"
    )
    server_action_create.add_argument("--name", type=str, required=True)
    image_or_snapshot = server_action_create.add_mutually_exclusive_group(required=True)
    image_or_snapshot.add_argument("--snapshot", type=str, default="")
    image_or_snapshot.add_argument("--image", type=str, default="")
    server_action_create.add_argument("--flavorid", type=str, required=True)
    server_action_create.add_argument(
        "--firewall", type=str, required=False, default="default"
    )
    password_or_sshkey = server_action_create.add_mutually_exclusive_group(
        required=True
    )
    password_or_sshkey.add_argument("--password", type=str, default="")
    password_or_sshkey.add_argument("--sshkey", type=str, default="")
    server_action_create.add_argument(
        "--wait", action="store_true", default=False, help="wait until server is active"
    )
    server_action_create.set_defaults(func=Servers.create_resource)

    server_action_delete = server_actions.add_parser(
        Action.DELETE, help="delete a server"
    )
    id_or_name = server_action_delete.add_mutually_exclusive_group(required=True)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    server_action_delete.set_defaults(func=Servers().delete_resource)

    server_action_list = server_actions.add_parser(Action.LIST, help="list servers")
    id_or_name = server_action_list.add_mutually_exclusive_group(required=False)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    server_action_list.set_defaults(func=Servers().list_resources)
