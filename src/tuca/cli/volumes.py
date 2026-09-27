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


def list_volumes(args: argparse.Namespace):
    list_resources(Client(get_token(None)).volumes, args)


def add_command_volumes(subparser: argparse._SubParsersAction):
    volumes = subparser.add_parser("volumes", help="volume sizes")
    volumes_actions = volumes.add_subparsers(help="available commands")
    volumes_action_list = volumes_actions.add_parser(
        Command.LIST, help="list volume sizes"
    )
    volumes_action_list.set_defaults(func=list_volumes)
