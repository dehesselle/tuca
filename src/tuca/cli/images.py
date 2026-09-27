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


def list_images(args: argparse.Namespace):
    list_resources(Client(get_token(None)).images, args)


def add_command_images(subparser: argparse._SubParsersAction):
    images = subparser.add_parser("images", help="server OS images")
    images_actions = images.add_subparsers(help="available commands")
    images_action_list = images_actions.add_parser(Command.LIST, help="list images")
    id_or_name = images_action_list.add_mutually_exclusive_group(required=False)
    id_or_name.add_argument("--id", type=str, default="")
    id_or_name.add_argument("--name", type=str, default="")
    images_action_list.add_argument(
        "--filter",
        type=str,
        default="",
        required=False,
        help="case-insensitive matching with name and id",
    )
    images_action_list.set_defaults(func=list_images)
