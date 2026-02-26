# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from .endpoint import Endpoint
from .resource import IdentifiableResource


class Command(StrEnum):
    LIST = auto()


class Status(StrEnum):
    PENDING = auto()
    IN_PROGRESS = "inProgress"
    COMPLETED = auto()
    ERRORED = auto()


class Action(
    IdentifiableResource
):  # TODO: Action is not really a resource, but because of the current
    # inheritance model, we're making it one. Better solution?
    status: Status
    type: str
    startedAt: str
    completedAt: str | None
    resourceId: str
    resourceType: str


class Actions(Endpoint[Action]):
    def __init__(self):
        super().__init__(Action, "actions")


def list_actions(args: argparse.Namespace):
    Actions().list_resources(args)


def setup_actions_endpoint(subparser: argparse._SubParsersAction):
    actions = subparser.add_parser("actions", help="list actions")
    snapshot_actions = actions.add_subparsers(help="available commands")
    snapshot_action_list = snapshot_actions.add_parser(
        Command.LIST, help="list actions"
    )
    snapshot_action_list.add_argument("--id", type=str, default="", required=False)
    snapshot_action_list.set_defaults(func=list_actions)
