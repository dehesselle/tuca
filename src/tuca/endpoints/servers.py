# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import platform
import signal
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from enum import StrEnum, auto

from pydantic import BaseModel
from slugify import slugify

from tuca.resources.action import Action
from tuca.resources.server import Server, Status

from .endpoint import Endpoint, EndpointError, ResourceNotFoundError, list_resources
from .firewalls import Firewalls
from .flavors import Flavors
from .images import Images
from .snapshots import Snapshots
from .volumes import Volumes


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


class CreateServerRequest(BaseModel):
    accessConfiguration: AccessConfiguration
    flavorId: str
    hostname: str
    name: str
    publicPortFirewallIds: list[str]
    volume: Volume


class CreateServerError(EndpointError):
    pass


class Servers(Endpoint[Server]):
    """
    Interact with the `servers`_ endpoint.

    .. _servers:
       https://api.clouding.io/docs/#tag/Servers
    """

    def __init__(self):
        super().__init__(Server, "servers")

    def create(
        self,
        name: str,
        hostname: str,
        flavor_id: str,
        snapshot: str,
        image: str,
        volume_ssdgb: int,
        password: str,
        sshkey_id: str,
        firewall: str,
        wait_until_active: bool = False,
    ):
        if flavor_id not in Flavors().all:
            raise CreateServerError(f"flavor not supported: {flavor_id}")

        if firewall:
            if matched_firewalls := [
                _ for _ in Firewalls().get() if firewall == _.id or firewall == _.name
            ]:
                if len(matched_firewalls) > 1:
                    raise CreateServerError(f"multiple firewalls matched: {firewall}")

                firewall_id = matched_firewalls[0].id
            else:
                raise CreateServerError(f"firewall not found: {firewall}")
        else:
            raise CreateServerError("firewall not specified")

        if volume_ssdgb and volume_ssdgb not in Volumes().all:
            raise CreateServerError(f"volume size not supported: {volume_ssdgb}")

        if snapshot:
            if matched_snapshots := [
                _ for _ in Snapshots().get() if snapshot == _.id or snapshot == _.name
            ]:
                if len(matched_snapshots) > 1:
                    raise CreateServerError(f"multiple snapshots matched: {snapshot}")

                volume = Volume(
                    source="snapshot",
                    id=matched_snapshots[0].id,
                    ssdGb=matched_snapshots[0].sizeGb,
                )
            else:
                raise CreateServerError(f"snapshot not found: {snapshot}")
        elif image:
            if matched_images := [
                _ for _ in Images().get() if image == _.id or image == _.name
            ]:
                if len(matched_images) > 1:
                    raise CreateServerError(f"multiple images matched: {image}")

                volume = Volume(
                    source="image",
                    id=matched_images[0].id,
                    ssdGb=matched_images[0].minimumSizeGb,
                )
            else:
                raise CreateServerError(f"image not found: {image}")
        else:
            raise CreateServerError("missing mandatory option: {image,snapshot}")

        if volume_ssdgb and volume_ssdgb > volume.ssdGb:
            volume.ssdGb = volume_ssdgb

        if password:
            access_configuration = AccessConfiguration(
                sshKeyId=None, password=password, savePassword=True
            )
        elif sshkey_id:
            access_configuration = AccessConfiguration(
                sshKeyId=sshkey_id, password=None, savePassword=False
            )
        else:
            raise CreateServerError("missing mandatory option: {password,sshkey}")

        self._create(
            CreateServerRequest(
                accessConfiguration=access_configuration,
                flavorId=flavor_id,
                hostname=slugify(hostname if hostname else name),
                name=name,
                publicPortFirewallIds=[firewall_id],
                volume=volume,
            )
        )

        if self.resources:
            if wait_until_active:
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

            print(self.to_str())
        else:
            raise CreateServerError("failed to create server")

    def start(self, id: str) -> Action:
        self.clouding.post(self.resource / id / "start")
        return self._deserialize_action()

    def stop(self, id: str) -> Action:
        self.clouding.post(self.resource / id / "stop")
        return self._deserialize_action()


def create_server(args: argparse.Namespace):
    Servers().create(
        name=args.name,
        hostname=args.hostname,
        flavor_id=args.flavorid,
        snapshot=args.snapshot,
        image=args.image,
        volume_ssdgb=args.ssdgb,
        password=args.password,
        sshkey_id=args.sshkey,
        firewall=args.firewall,
        wait_until_active=args.wait,
    )


def delete_server(args: argparse.Namespace):
    if args.name:
        Servers().delete_by_name(args.name)
    else:
        Servers().delete(args.id)


def list_servers(args: argparse.Namespace):
    list_resources(Servers(), args)


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
        raise ResourceNotFoundError("server not found")


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
        raise ResourceNotFoundError("server not found")


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
