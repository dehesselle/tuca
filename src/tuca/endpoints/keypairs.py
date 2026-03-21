# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from tuca.resources.keypair import Keypair

from .endpoint import Endpoint, RequestPayload


class Command(StrEnum):
    CREATE = auto()
    DELETE = auto()
    LIST = auto()


class Keypairs(Endpoint[Keypair]):
    """ssh `keys`_

    .. _keys:
       https://api.clouding.io/docs/#tag/SSH-Keys
    """

    def __init__(self):
        super().__init__(Keypair, "keypairs")
        self.response_key = "values"

    def create_resource(self, args):
        payload = CreateRequestPayload(
            name=args.name, publicKey=args.publickey, privateKey=args.privatekey
        )
        self.create(payload)
        print(self.to_str(self.resources))


class CreateRequestPayload(RequestPayload):
    name: str
    publicKey: str
    privateKey: str


def create_keypair(args: argparse.Namespace):
    Keypairs().create_resource(args)


def delete_keypair(args: argparse.Namespace):
    Keypairs().delete_resource(args)


def list_keypairs(args: argparse.Namespace):
    Keypairs().list_resources(args)


def setup_keypairs_cli(subparser: argparse._SubParsersAction):
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
