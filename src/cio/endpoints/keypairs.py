from argparse import _SubParsersAction
from enum import StrEnum, auto

from cio.resource import Resource

from .endpoint import Endpoint, RequestPayload


class Action(StrEnum):
    CREATE = auto()
    DELETE = auto()
    LIST = auto()


class Keypair(Resource):
    id: str
    name: str
    fingerprint: str


class Keypairs(Endpoint[Keypair]):
    def __init__(self):
        super().__init__(Keypair, "keypairs")
        self.response_key = "values"


class CreateRequestPayload(RequestPayload):
    name: str
    publicKey: str
    privateKey: str


def create_keypair(args):
    payload = CreateRequestPayload(
        name=args.name, publicKey=args.publickey, privateKey=args.privatekey
    )
    keypairs = Keypairs()
    keypair = keypairs.create(payload)
    print(keypairs.to_str(keypair))


def delete_keypair(args):
    keypairs = Keypairs()
    if args.name:
        if keypair := keypairs.get_by_name(args.name):
            keypair_id = keypair.id
        else:
            keypair_id = ""
    else:
        keypair_id = args.id

    if keypair_id:
        response = keypairs.delete(keypair_id)
        print(keypairs.to_str(response))
        # TODO not checking anything
    else:
        print("not found - no delete")  # TODO
        exit(1)


def list_keypair(args):
    keypairs = Keypairs()
    if args.id:
        print(keypairs.to_str(keypairs.get_by_id(args.id)))
    else:
        print(keypairs.to_str())


def setup_keypairs_endpoint(subparser: _SubParsersAction):
    snapshots = subparser.add_parser("keypairs", help="manage keypairs")
    keypair_actions = snapshots.add_subparsers(help="available actions")

    keypair_action_create = keypair_actions.add_parser(
        Action.CREATE, help="create new server"
    )
    keypair_action_create.add_argument("--name", type=str, required=True)
    keypair_action_create.add_argument("--publickey", type=str, required=True)
    keypair_action_create.add_argument("--privatekey", type=str, default="")
    keypair_action_create.set_defaults(func=create_keypair)

    keypair_action_delete = keypair_actions.add_parser(
        Action.DELETE, help="delete a server"
    )
    id_or_name = keypair_action_delete.add_mutually_exclusive_group(required=True)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    keypair_action_delete.set_defaults(func=delete_keypair)

    keypair_action_list = keypair_actions.add_parser(Action.LIST, help="list keypairs")
    keypair_action_list.add_argument("-i", "--id", default="", required=False)
    keypair_action_list.set_defaults(func=list_keypair)
