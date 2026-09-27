# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from tuca.cli.auth import get_token
from tuca.cli.endpoint import list_resources
from tuca.cli.output import to_str
from tuca.client import Client


class Command(StrEnum):
    CREATE = auto()
    DELETE = auto()
    LIST = auto()


def create_keypair(args: argparse.Namespace):
    keypairs = Client(get_token(None)).keypairs
    keypair = keypairs.create(args.name, args.publickey, args.privatekey)
    print(to_str(keypairs, [keypair] if keypair else []))


def delete_keypair(args: argparse.Namespace):
    client = Client(get_token(None))
    if args.name:
        client.keypairs.delete_by_name(args.name)
    else:
        client.keypairs.delete(args.id)


def list_keypairs(args: argparse.Namespace):
    list_resources(Client(get_token(None)).keypairs, args)


def add_command_keypairs(subparser: argparse._SubParsersAction):
    snapshots = subparser.add_parser("keypairs", help="SSH keys")
    keypair_actions = snapshots.add_subparsers(help="available commands")

    keypair_action_create = keypair_actions.add_parser(
        Command.CREATE, help="create new SSH key"
    )
    keypair_action_create.add_argument("--name", type=str, required=True)
    keypair_action_create.add_argument("--publickey", type=str, required=True)
    keypair_action_create.add_argument("--privatekey", type=str, default="")
    keypair_action_create.set_defaults(func=create_keypair)

    keypair_action_delete = keypair_actions.add_parser(
        Command.DELETE, help="delete SSH key"
    )
    id_or_name = keypair_action_delete.add_mutually_exclusive_group(required=True)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    keypair_action_delete.set_defaults(func=delete_keypair)

    keypair_action_list = keypair_actions.add_parser(Command.LIST, help="list SSH keys")
    id_or_name = keypair_action_list.add_mutually_exclusive_group(required=False)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    keypair_action_list.add_argument(
        "--filter",
        type=str,
        default="",
        required=False,
        help="case-insensitive matching with name and id",
    )
    keypair_action_list.set_defaults(func=list_keypairs)
