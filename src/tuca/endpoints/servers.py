# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import logging
import platform
import signal
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from enum import StrEnum, auto

from pydantic import BaseModel
from slugify import slugify

from tuca.resources.server import Server, Status

from .endpoint import Endpoint, RequestPayload
from .firewalls import Firewalls
from .flavors import Flavors
from .images import Images
from .snapshots import Snapshots
from .volumes import Volumes

log = logging.getLogger("servers")


class Command(StrEnum):
    CREATE = auto()
    DELETE = auto()
    LIST = auto()
    START = auto()
    STOP = auto()


class AccessConfiguration(BaseModel):
    password: str | None
    savePassword: bool
    sshKeyId: str | None


class Volume(BaseModel):
    id: str
    source: str
    ssdGb: int


class CreateRequestPayload(RequestPayload):
    accessConfiguration: AccessConfiguration
    flavorId: str
    hostname: str
    name: str
    publicPortFirewallIds: list[str]
    volume: Volume


class Servers(Endpoint[Server]):
    """
    Interact with the `servers`_ endpoint.

    .. _servers:
       https://api.clouding.io/docs/#tag/Servers
    """

    def __init__(self):
        super().__init__(Server, "servers")

    def create_resource(self, args):
        if args.flavorid not in Flavors().all:
            log.error(f"flavor not supported: {args.flavorid}")
            exit(1)

        if args.snapshot:
            if snapshots := [
                snapshot
                for snapshot in Snapshots().get()
                if args.snapshot == snapshot.id or args.snapshot == snapshot.name
            ]:
                if len(snapshots) > 1:
                    log.error(f"multiple snapshots matched: {args.snapshot}")
                    exit(1)

                volume = Volume(
                    source="snapshot", id=snapshots[0].id, ssdGb=snapshots[0].sizeGb
                )
            else:
                log.error(f"snapshot not found: {args.snapshot}")
                exit(1)
        elif args.image:
            if images := [
                image
                for image in Images().get()
                if args.image == image.id or args.image == image.name
            ]:
                if len(images) > 1:
                    log.error(f"multiple images matched: {args.image}")
                    exit(1)

                volume = Volume(
                    source="image", id=images[0].id, ssdGb=images[0].minimumSizeGb
                )
            else:
                log.error(f"image not found: {args.image}")
                exit(1)
        else:
            log.error("missing mandatory option: snapshot|image")
            exit(1)

        if args.ssdgb:
            if args.ssdgb not in Volumes().all:
                log.error(f"volume size not supported: {args.ssdgb}")
                exit(1)
            volume.ssdGb = args.ssdgb

        if args.password:
            access_configuration = AccessConfiguration(
                sshKeyId=None, password=args.password, savePassword=True
            )
        elif args.sshkey:
            access_configuration = AccessConfiguration(
                sshKeyId=args.sshkey, password=None, savePassword=False
            )
        else:
            log.error("missing mandatory option: password|sshkey")
            exit(1)

        if firewalls := [
            firewall
            for firewall in Firewalls().get()
            if args.firewall == firewall.id or args.firewall == firewall.name
        ]:
            if len(firewalls) > 1:
                log.error(f"multiple firewalls matched: {args.firewall}")
                exit(1)

            firewall_id = firewalls[0].id
        else:
            log.error(f"firewall not found: {args.firewall}")
            exit(1)

        payload = CreateRequestPayload(
            name=args.name,
            hostname=slugify(args.hostname if args.hostname else args.name),
            flavorId=args.flavorid,
            accessConfiguration=access_configuration,
            volume=volume,
            publicPortFirewallIds=[firewall_id],
        )
        self.create(payload)
        if self.resources:
            if args.wait:
                if platform.system() == "Windows":
                    signal.signal(signal.SIGINT, signal.SIG_DFL)  # make ctrl+c work
                with ThreadPoolExecutor() as executor:

                    def wait(servers: Servers, status: Status, seconds: int) -> None:
                        while server := servers.get_one(servers.resources[0].id):
                            if server.status == status:
                                break
                            time.sleep(seconds)

                    future = executor.submit(wait, self, Status.ACTIVE, 15)
                    try:
                        future.result(timeout=300)
                    except TimeoutError:
                        future.cancel()
            print(self.to_str(self.resources))
        else:
            log.error("failed to create server")
            exit(1)

    def start(self, id: str):
        self.clouding.post(self.resource / id / "start")
        print(self._to_str(self._deserialize_action().as_dict))

    def stop(self, id: str):
        self.clouding.post(self.resource / id / "stop")
        print(self._to_str(self._deserialize_action().as_dict))


def create_server(args: argparse.Namespace):
    Servers().create_resource(args)


def delete_server(args: argparse.Namespace):
    Servers().delete_resource(args)


def list_servers(args: argparse.Namespace):
    Servers().list_resources(args)


def start_server(args: argparse.Namespace):
    servers = Servers()
    server = None
    if hasattr(args, "id") and args.id:
        server = servers.get_one(args.id)
    elif hasattr(args, "name") and args.name:
        server = servers.get_one_by_name(args.name)

    if server:
        servers.start(server.id)
    else:
        log.error("server not found")


def stop_server(args: argparse.Namespace):
    servers = Servers()
    server = None
    if hasattr(args, "id") and args.id:
        server = servers.get_one(args.id)
    elif hasattr(args, "name") and args.name:
        server = servers.get_one_by_name(args.name)

    if server:
        servers.stop(server.id)
    else:
        log.error("server not found")


def setup_servers_cli(subparser: argparse._SubParsersAction):
    servers = subparser.add_parser("servers", help="server instances")
    server_actions = servers.add_subparsers(help="available commands")

    server_action_create = server_actions.add_parser(
        Command.CREATE, help="create new server"
    )
    server_action_create.add_argument("--name", type=str, required=True)
    server_action_create.add_argument(
        "--hostname", type=str, required=False, default=""
    )
    image_or_snapshot = server_action_create.add_mutually_exclusive_group(required=True)
    image_or_snapshot.add_argument("--snapshot", type=str, default="")
    image_or_snapshot.add_argument("--image", type=str, default="")
    server_action_create.add_argument(
        "--ssdgb", type=int, required=False, default=0, help="size of system disk"
    )
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
    server_action_create.set_defaults(func=create_server)

    server_action_delete = server_actions.add_parser(
        Command.DELETE, help="delete server"
    )
    id_or_name = server_action_delete.add_mutually_exclusive_group(required=True)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    server_action_delete.set_defaults(func=delete_server)

    server_action_list = server_actions.add_parser(Command.LIST, help="list servers")
    id_or_name = server_action_list.add_mutually_exclusive_group(required=False)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    server_action_list.add_argument(
        "--filter",
        type=str,
        default="",
        required=False,
        help="case-insensitive matching with name and id",
    )
    server_action_list.set_defaults(func=list_servers)

    server_action_start = server_actions.add_parser(Command.START, help="start server")
    id_or_name = server_action_start.add_mutually_exclusive_group(required=False)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    server_action_start.set_defaults(func=start_server)

    server_action_stop = server_actions.add_parser(Command.STOP, help="stop server")
    id_or_name = server_action_stop.add_mutually_exclusive_group(required=False)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    server_action_stop.set_defaults(func=stop_server)
