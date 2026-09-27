# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import platform
import signal
from enum import StrEnum, auto

from tuca.cli.auth import get_token
from tuca.client import Client
from tuca.endpoints.endpoint import ResourceNotFoundError, list_resources


class Command(StrEnum):
    CREATE = auto()
    DELETE = auto()
    LIST = auto()
    START = auto()
    STOP = auto()


def create_server(args: argparse.Namespace):
    if args.wait and platform.system() == "Windows":
        signal.signal(signal.SIGINT, signal.SIG_DFL)  # make ctrl+c work

    servers = Client(get_token(None)).servers
    server = servers.create(
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
    print(servers.to_str([server]))


def delete_server(args: argparse.Namespace):
    servers = Client(get_token(None)).servers
    if args.name:
        servers.delete_by_name(args.name)
    else:
        servers.delete(args.id)


def list_servers(args: argparse.Namespace):
    list_resources(Client(get_token(None)).servers, args)


def start_server(args: argparse.Namespace):
    servers = Client(get_token(None)).servers
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
    servers = Client(get_token(None)).servers
    server = None
    if hasattr(args, "id") and args.id:
        server = servers.get_one(args.id)
    elif hasattr(args, "name") and args.name:
        server = servers.get_one_by_name(args.name)

    if server:
        servers.stop(server.id)
    else:
        raise ResourceNotFoundError("server not found")


def add_command_servers(subparser: argparse._SubParsersAction):
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
