# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from enum import StrEnum, auto

from .endpoint import Endpoint
from .resource import IdentifiableResource, Resource


class Action(StrEnum):
    LIST = auto()


class Flavor(IdentifiableResource):
    vCores: float
    ramGb: int
    pricePerHour: float
    pricePerMonthApprox: float


class VolumeSize(Resource):
    storageType: str
    sizeGb: int
    pricePerHour: float
    pricePerMonthApprox: float


class Flavors(Endpoint[Flavor]):
    def __init__(self):
        super().__init__(Flavor, "sizes/flavors")
        self.response_key = "flavors"

    @property
    def all(self) -> list[str]:
        self.get()
        return [flavor.id for flavor in self.resources]


class Sizes(Endpoint[VolumeSize]):
    def __init__(self):
        super().__init__(VolumeSize, "sizes/volumes")
        self.response_key = "volumeSizes"


def list_flavors(args: argparse.Namespace):
    Flavors().list_resources(args)


def list_sizes(args: argparse.Namespace):
    Sizes().list_resources(args)


def setup_sizes_endpoint(subparser: argparse._SubParsersAction):
    volumesizes = subparser.add_parser("volumesizes", help="query volume sizes")
    volumesizes_actions = volumesizes.add_subparsers(help="available actions")
    volumesizes_action_list = volumesizes_actions.add_parser(
        Action.LIST, help="list volume sizes"
    )
    volumesizes_action_list.set_defaults(func=list_sizes)

    flavors = subparser.add_parser("flavors", help="query cpu/memory sizes")
    flavors_actions = flavors.add_subparsers(help="available actions")
    flavors_action_list = flavors_actions.add_parser(
        Action.LIST, help="list server sizes"
    )
    flavors_action_list.set_defaults(func=list_flavors)
