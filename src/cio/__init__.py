import argparse
from enum import StrEnum, auto

from cio.auth import delete_token, set_token
from cio.config import config
from cio.servers import Servers
from cio.snapshots import Snapshots
from cio.version import VERSION


class Component(StrEnum):
    AUTH = auto()
    LIMITS = auto()
    SERVERS = auto()
    SNAPSHOTS = auto()


class Action(StrEnum):
    LIST = auto()
    CREATE = auto()
    SET = auto()
    DELETE = auto()


def list_servers(args):
    servers = Servers()
    servers.list(args.id)


def list_snapshots(args):
    snpashots = Snapshots()
    snpashots.list(args.id)


def main() -> None:
    parser = argparse.ArgumentParser(description="unofficial CLI for Clouding.io")
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="make output verbose"
    )
    parser.add_argument("--version", action="version", version=f"cio {VERSION}")
    components = parser.add_subparsers(help="manageable components", dest="component")

    auth = components.add_parser(Component.AUTH, help="manage authentication token")
    auth_actions = auth.add_subparsers()
    auth_action_set = auth_actions.add_parser(
        Action.SET, help="set authentication token"
    )
    auth_action_set.set_defaults(func=set_token)
    auth_action_delete = auth_actions.add_parser(
        Action.DELETE, help="delete authentication token"
    )
    auth_action_delete.set_defaults(func=delete_token)

    servers = components.add_parser(Component.SERVERS, help="manage servers")
    server_actions = servers.add_subparsers(help="available actions")
    # server_action_create = server_actions.add_parser(
    #     Action.CREATE,
    #     help="create servers",
    # )
    server_action_list = server_actions.add_parser(Action.LIST, help="list servers")
    server_action_list.add_argument("-i", "--id", default="", required=False)
    server_action_list.set_defaults(func=list_servers)

    snapshots = components.add_parser(Component.SNAPSHOTS, help="manage snapshots")
    snapshot_actions = snapshots.add_subparsers(help="available actions")
    snapshot_action_list = snapshot_actions.add_parser(
        Action.LIST, help="list snapshots"
    )
    snapshot_action_list.add_argument("-i", "--id", default="", required=False)
    snapshot_action_list.set_defaults(func=list_snapshots)

    args = parser.parse_args()
    config.be_verbose = args.verbose
    try:
        args.func(args)
    except AttributeError:
        parser.print_usage()
