# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from tuca.cli.auth import get_token
from tuca.client import Client
from tuca.endpoints.endpoint import list_resources


class Command(StrEnum):
    LIST = auto()


def list_snapshots(args: argparse.Namespace):
    list_resources(Client(get_token(None)).snapshots, args)


def add_command_snapshots(subparser: argparse._SubParsersAction):
    snapshots = subparser.add_parser("snapshots", help="server snapshots")
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
