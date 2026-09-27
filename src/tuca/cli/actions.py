# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from tuca.client import Client
from tuca.clouding.auth import get_token
from tuca.endpoints.endpoint import list_resources


class Command(StrEnum):
    LIST = auto()


def list_actions(args: argparse.Namespace):
    list_resources(Client(get_token(None)).actions, args)


def add_command_actions(subparser: argparse._SubParsersAction):
    actions = subparser.add_parser("actions", help="long-running actions")
    snapshot_actions = actions.add_subparsers(help="available commands")
    snapshot_action_list = snapshot_actions.add_parser(
        Command.LIST, help="list actions"
    )
    snapshot_action_list.add_argument("--id", type=str, default="", required=False)
    snapshot_action_list.set_defaults(func=list_actions)
