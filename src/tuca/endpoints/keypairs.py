# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from argparse import _SubParsersAction
from enum import StrEnum, auto

from .endpoint import Endpoint, RequestPayload
from .resource import NamedResource


class Action(StrEnum):
    CREATE = auto()
    DELETE = auto()
    LIST = auto()


class Keypair(NamedResource):
    fingerprint: str


class Keypairs(Endpoint[Keypair]):
    def __init__(self):
        super().__init__(Keypair, "keypairs")
        self.response_key = "values"

    @classmethod
    def create_resource(cls, args):
        payload = CreateRequestPayload(
            name=args.name, publicKey=args.publickey, privateKey=args.privatekey
        )
        keypairs = Keypairs()
        keypairs.create(payload)
        print(keypairs.to_str())


class CreateRequestPayload(RequestPayload):
    name: str
    publicKey: str
    privateKey: str


def setup_keypairs_endpoint(subparser: _SubParsersAction):
    snapshots = subparser.add_parser("keypairs", help="manage keypairs")
    keypair_actions = snapshots.add_subparsers(help="available actions")

    keypair_action_create = keypair_actions.add_parser(
        Action.CREATE, help="create new server"
    )
    keypair_action_create.add_argument("--name", type=str, required=True)
    keypair_action_create.add_argument("--publickey", type=str, required=True)
    keypair_action_create.add_argument("--privatekey", type=str, default="")
    keypair_action_create.set_defaults(func=Keypairs.create_resource)

    keypair_action_delete = keypair_actions.add_parser(
        Action.DELETE, help="delete a server"
    )
    id_or_name = keypair_action_delete.add_mutually_exclusive_group(required=True)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    keypair_action_delete.set_defaults(func=Keypairs().delete_resource)

    keypair_action_list = keypair_actions.add_parser(Action.LIST, help="list keypairs")
    keypair_action_list.add_argument("-i", "--id", default="", required=False)
    keypair_action_list.set_defaults(func=Keypairs().list_resources)
