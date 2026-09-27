# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from tuca.cli.endpoint import list_resources
from tuca.client import Client


class Command(StrEnum):
    LIST = auto()


def list_flavors(client: Client, args: argparse.Namespace):
    list_resources(client.flavors, args)


def add_command_flavors(subparser: argparse._SubParsersAction):
    flavors = subparser.add_parser("flavors", help="sizing as cpu/memory combinations")
    flavors_actions = flavors.add_subparsers(help="available commands")
    flavors_action_list = flavors_actions.add_parser(
        Command.LIST, help="list available flavors"
    )
    flavors_action_list.set_defaults(func=list_flavors)
