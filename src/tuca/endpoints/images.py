# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from tuca.resources.image import Image

from .endpoint import Endpoint, list_resources


class Command(StrEnum):
    LIST = auto()


class Images(Endpoint[Image]):
    """
    Interact with the `images`_ endpoint.

    .. _images:
       https://api.clouding.io/docs/#tag/Images
    """

    def __init__(self):
        super().__init__(Image, "images")


def list_images(args: argparse.Namespace):
    list_resources(Images(), args)


def setup_images_cli(subparser: argparse._SubParsersAction):
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
