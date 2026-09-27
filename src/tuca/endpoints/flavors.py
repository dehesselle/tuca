# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from tuca.resources.flavor import Flavor

from .endpoint import Endpoint

if TYPE_CHECKING:
    from tuca.client import Client


class Flavors(Endpoint[Flavor]):
    """server `sizes` as cpu/ram combos_

    .. _sizes:
       https://api.clouding.io/docs/#tag/Sizes/operation/ListAllFlavors
    """

    def __init__(self, client: Client):
        super().__init__(Flavor, "sizes/flavors", client)
        self.response_key = "flavors"

    @property
    def all(self) -> list[str]:
        self.get()
        return [flavor.id for flavor in self.resources]
