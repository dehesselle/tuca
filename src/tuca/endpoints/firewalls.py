# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from tuca.resources.firewall import Firewall

from .endpoint import Endpoint

if TYPE_CHECKING:
    from tuca.client import Client


class Firewalls(Endpoint[Firewall]):
    """
    Interact with the `firewalls`_ endpoint.

    .. _firewalls:
       https://api.clouding.io/docs/#tag/Firewalls
    """

    def __init__(self, client: Client | None = None):
        super().__init__(Firewall, "firewalls", client)
        self.response_key = "values"
