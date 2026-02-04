# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from argparse import _SubParsersAction
from enum import StrEnum, auto

from cio.resource import Resource

from .endpoint import Endpoint
from .images import Image


class Action(StrEnum):
    LIST = auto()


class Snapshot(Resource):
    id: str
    name: str
    createdAt: str
    sizeGb: int
    image: Image


class Snapshots(Endpoint[Snapshot]):
    def __init__(self):
        super().__init__(Snapshot, "snapshots")


def setup_snapshots_endpoint(subparser: _SubParsersAction):
    snapshots = subparser.add_parser("snapshots", help="manage snapshots")
    snapshot_actions = snapshots.add_subparsers(help="available actions")
    snapshot_action_list = snapshot_actions.add_parser(
        Action.LIST, help="list snapshots"
    )
    snapshot_action_list.set_defaults(func=Snapshots.list_resources)
