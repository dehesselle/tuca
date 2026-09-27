# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from tuca.resources.action import Action

from .endpoint import Endpoint

if TYPE_CHECKING:
    from tuca.client import Client


class Actions(Endpoint[Action]):
    """
    Interact with the `actions`_ endpoint.

    .. _actions:
       https://api.clouding.io/docs/#tag/Actions
    """

    def __init__(self, client: Client):
        super().__init__(Action, "actions", client)
