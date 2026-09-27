# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING

from tuca.endpoints.endpoint import index_by_id

if TYPE_CHECKING:
    from tuca.client import Client


class Expense(StrEnum):
    IMAGES = auto()
    SERVERS = auto()
    SNAPSHOTS = auto()
    TOTAL = auto()


def compute_hourly_cost(client: Client) -> dict[str, float]:
    """collect incurring cost of all resources

    This accounts only for images, servers and snapshots.
    """
    cost = {
        Expense.IMAGES.value: 0.0,
        Expense.SERVERS.value: 0.0,
        Expense.SNAPSHOTS.value: 0.0,
        Expense.TOTAL.value: 0.0,
    }

    flavors = index_by_id(client.flavors.get())
    images = index_by_id(client.images.get())
    for server in client.servers.get():
        cost[Expense.SERVERS] += flavors[server.flavor].pricePerHour
        cost[Expense.IMAGES] += images[server.image.id].pricePerHour
    for snapshot in client.snapshots.get():
        cost[Expense.SNAPSHOTS] += snapshot.cost.pricePerHour

    cost[Expense.TOTAL] = sum(cost.values())
    return cost
