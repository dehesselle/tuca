# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from tuca.endpoints.endpoint import index_by_id
from tuca.resources.server import Server

if TYPE_CHECKING:
    from tuca.client import Client


class Cost:
    """hourly cost of resources as Clouding bills them (net prices)

    This is not an endpoint of its own; it combines the prices from the
    flavors, images, volumes and snapshots endpoints.
    """

    def __init__(self, client: Client):
        self.client = client

    def server(self, server: Server) -> float:
        """price of one server per hour: flavor, image license and disk"""
        return self.servers([server])

    def servers(self, servers: list[Server] | None = None) -> float:
        """price of servers per hour (default: all): flavors, image licenses and disks"""
        flavors = index_by_id(self.client.flavors.get())
        images = index_by_id(self.client.images.get())
        volumes = {volume.sizeGb: volume for volume in self.client.volumes.get()}
        total = 0.0
        for server in self.client.servers.get() if servers is None else servers:
            image = images[server.image.id]
            match image.billingUnit:
                case None:
                    image_price = image.pricePerHour
                case "Core":  # e.g. Windows licenses
                    image_price = image.pricePerHour * server.vCores
                case unit:
                    raise ValueError(
                        f"unknown billing unit {unit!r} of image {image.id}"
                    )
            total += (
                flavors[server.flavor].pricePerHour
                + image_price
                + volumes[server.volumeSizeGb].pricePerHour
            )
        return total

    def snapshots(self) -> float:
        """price of all snapshots per hour"""
        return sum(
            snapshot.cost.pricePerHour for snapshot in self.client.snapshots.get()
        )
