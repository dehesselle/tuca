from argparse import _SubParsersAction
from enum import StrEnum, auto

from cio.component import Component, Components


class Action(StrEnum):
    LIST = auto()


class Snapshot(Component):
    createdAt: str


class Snapshots(Components):
    def __init__(self):
        super().__init__(Snapshot, "snapshots")


def list_snapshot(args):
    snapshots = Snapshots()
    if args.id:
        print(snapshots.to_str(snapshots.get_by_id(args.id)))
    else:
        print(snapshots.to_str())


def setup_snapshots_cli(subparser: _SubParsersAction):
    snapshots = subparser.add_parser("snapshots", help="manage snapshots")
    snapshot_actions = snapshots.add_subparsers(help="available actions")
    snapshot_action_list = snapshot_actions.add_parser(
        Action.LIST, help="list snapshots"
    )
    snapshot_action_list.add_argument("-i", "--id", default="", required=False)
    snapshot_action_list.set_defaults(func=list_snapshot)
