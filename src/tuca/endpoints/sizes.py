# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from tuca.resources.flavor import Flavor
from tuca.resources.volumesize import VolumeSize

from .endpoint import Endpoint


class Command(StrEnum):
    LIST = auto()


class Flavors(Endpoint[Flavor]):
    """server `sizes`_

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


class VolumeSizes(Endpoint[VolumeSize]):
    """volume `sizes`_

    .. _sizes:
      https://api.clouding.io/docs/#tag/Sizes/operation/ListAllVolumeSizes
    """

    def __init__(self):
        super().__init__(VolumeSize, "sizes/volumes")
        self.response_key = "volumeSizes"

    @property
    def all(self) -> list[int]:
        self.get()
        return [volumesize.sizeGb for volumesize in self.resources]


def list_flavors(args: argparse.Namespace):
    Flavors().list_resources(args)


def list_volume_sizes(args: argparse.Namespace):
    VolumeSizes().list_resources(args)


def setup_sizes_endpoint(subparser: argparse._SubParsersAction):
    volumesizes = subparser.add_parser("volumesizes", help="volume sizes")
    volumesizes_actions = volumesizes.add_subparsers(help="available commands")
    volumesizes_action_list = volumesizes_actions.add_parser(
        Command.LIST, help="list volume sizes"
    )
    volumesizes_action_list.set_defaults(func=list_volume_sizes)

    flavors = subparser.add_parser("flavors", help="cpu/memory combinations")
    flavors_actions = flavors.add_subparsers(help="available commands")
    flavors_action_list = flavors_actions.add_parser(
        Command.LIST, help="list available flavors"
    )
    flavors_action_list.set_defaults(func=list_flavors)
    flavors_action_list.set_defaults(func=list_flavors)
