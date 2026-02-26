# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from .endpoint import Endpoint
from .images import Image
from .resource import NamedResource


class Command(StrEnum):
    LIST = auto()


class Snapshot(NamedResource):
    createdAt: str
    sizeGb: int
    image: Image


class Snapshots(Endpoint[Snapshot]):
    def __init__(self):
        super().__init__(Snapshot, "snapshots")


def list_snapshots(args: argparse.Namespace):
    Snapshots().list_resources(args)


def setup_snapshots_endpoint(subparser: argparse._SubParsersAction):
    snapshots = subparser.add_parser("snapshots", help="manage snapshots")
    snapshot_actions = snapshots.add_subparsers(help="available commands")
    snapshot_action_list = snapshot_actions.add_parser(
        Command.LIST, help="list snapshots"
    )
    id_or_name = snapshot_action_list.add_mutually_exclusive_group(required=False)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    snapshot_action_list.add_argument(
        "--filter",
        type=str,
        default="",
        required=False,
        help="case-insensitive matching with name and id",
    )
    snapshot_action_list.set_defaults(func=list_snapshots)
