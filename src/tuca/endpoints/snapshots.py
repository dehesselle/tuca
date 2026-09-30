# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from tuca.resources.snapshot import Snapshot

from .endpoint import Endpoint

if TYPE_CHECKING:
    from tuca.client import Client


class Snapshots(Endpoint[Snapshot]):
    """
    Interact with the `snapshots`_ endpoint.

    .. _snapshots:
       https://api.clouding.io/docs/#tag/Snapshots
    """

    def __init__(self, client: Client):
        super().__init__(Snapshot, "snapshots", client)
