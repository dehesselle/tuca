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


def list_flavors(args: argparse.Namespace):
    list_resources(Client(get_token(None)).flavors, args)


def add_command_flavors(subparser: argparse._SubParsersAction):
    flavors = subparser.add_parser("flavors", help="sizing as cpu/memory combinations")
    flavors_actions = flavors.add_subparsers(help="available commands")
    flavors_action_list = flavors_actions.add_parser(
        Command.LIST, help="list available flavors"
    )
    flavors_action_list.set_defaults(func=list_flavors)
