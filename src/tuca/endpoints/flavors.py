# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from tuca.resources.flavor import Flavor

from .endpoint import Endpoint


class Command(StrEnum):
    LIST = auto()


class Flavors(Endpoint[Flavor]):
    """server `sizes` as cpu/ram combos_

    .. _sizes:
       https://api.clouding.io/docs/#tag/Sizes/operation/ListAllFlavors
    """

    def __init__(self):
        super().__init__(Flavor, "sizes/flavors")
        self.response_key = "flavors"

    @property
    def all(self) -> list[str]:
        self.get()
        return [flavor.id for flavor in self.resources]


def list_flavors(args: argparse.Namespace):
    Flavors().list_resources(args)


def setup_flavors_endpoint(subparser: argparse._SubParsersAction):
    flavors = subparser.add_parser("flavors", help="sizing as cpu/memory combinations")
    flavors_actions = flavors.add_subparsers(help="available commands")
    flavors_action_list = flavors_actions.add_parser(
        Command.LIST, help="list available flavors"
    )
    flavors_action_list.set_defaults(func=list_flavors)
    flavors_action_list.set_defaults(func=list_flavors)
