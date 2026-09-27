# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from tuca.cli.endpoint import list_resources
from tuca.client import Client


class Command(StrEnum):
    LIST = auto()


def list_firewalls(client: Client, args: argparse.Namespace):
    list_resources(client.firewalls, args)


def add_command_firewalls(subparser: argparse._SubParsersAction):
    firewalls = subparser.add_parser("firewalls", help="firewalls and rules")
    firewall_actions = firewalls.add_subparsers(help="available commands")

    firewall_action_list = firewall_actions.add_parser(
        Command.LIST, help="list firewalls"
    )
    id_or_name = firewall_action_list.add_mutually_exclusive_group(required=False)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    firewall_action_list.add_argument(
        "--filter",
        type=str,
        default="",
        required=False,
        help="case-insensitive matching with name and id",
    )
    firewall_action_list.set_defaults(func=list_firewalls)
