# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from tuca.resources.volumesize import VolumeSize

from .endpoint import Endpoint


class Command(StrEnum):
    LIST = auto()


class Volumes(Endpoint[VolumeSize]):
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


def list_volumes(args: argparse.Namespace):
    Volumes().list_resources(args)


def setup_volumes_endpoint(subparser: argparse._SubParsersAction):
    volumes = subparser.add_parser("volumes", help="volume sizes")
    volumes_actions = volumes.add_subparsers(help="available commands")
    volumes_action_list = volumes_actions.add_parser(
        Command.LIST, help="list volume sizes"
    )
    volumes_action_list.set_defaults(func=list_volumes)
