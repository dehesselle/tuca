# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from tuca.resources.image import Image

from .endpoint import Endpoint

if TYPE_CHECKING:
    from tuca.client import Client


class Images(Endpoint[Image]):
    """
    Interact with the `images`_ endpoint.

    .. _images:
       https://api.clouding.io/docs/#tag/Images
    """

    def __init__(self, client: Client):
        super().__init__(Image, "images", client)
