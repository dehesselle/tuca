# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import json
from argparse import _SubParsersAction
from enum import StrEnum, auto

from tuca.endpoints.flavors import Flavors
from tuca.endpoints.images import Images
from tuca.endpoints.servers import Servers
from tuca.endpoints.snapshots import Snapshots


class Expense(StrEnum):
    IMAGES = auto()
    SERVERS = auto()
    SNAPSHOTS = auto()
    TOTAL = auto()


def print_total_cost_per_hour(_) -> None:
    """collect incurring cost of all resources

    This accounts only for images, servers and snapshots.
    """
    servers = Servers()
    flavors = Flavors()
    images = Images()
    snapshots = Snapshots()

    cost = {
        Expense.IMAGES.value: 0.0,
        Expense.SERVERS.value: 0.0,
        Expense.SNAPSHOTS.value: 0.0,
        Expense.TOTAL.value: 0.0,
    }

    for server in servers.get():
        cost[Expense.SERVERS] += flavors.by_id[server.flavor].pricePerHour
        cost[Expense.IMAGES] += images.by_id[server.image.id].pricePerHour
    for snapshot in snapshots.get():
        cost[Expense.SNAPSHOTS] += snapshot.cost.pricePerHour

    cost[Expense.TOTAL] = sum(cost.values())
    print(
        json.dumps(
            {"cost": cost},
            indent=4,
            sort_keys=True,
        )
    )


def setup_cost_cli(subparser: _SubParsersAction):
    cost = subparser.add_parser("cost", help="hourly costs")
    cost.set_defaults(func=print_total_cost_per_hour)
