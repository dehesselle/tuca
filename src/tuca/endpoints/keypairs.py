# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from tuca.resources.keypair import Keypair

from .endpoint import Endpoint

if TYPE_CHECKING:
    from tuca.client import Client


class Keypairs(Endpoint[Keypair]):
    """ssh `keys`_

    .. _keys:
       https://api.clouding.io/docs/#tag/SSH-Keys
    """

    def __init__(self, client: Client):
        super().__init__(Keypair, "keypairs", client)
        self.response_key = "values"

    def create(
        self, name: str, public_key: str, private_key: str = ""
    ) -> Keypair | None:
        payload = CreateKeypairRequest(
            name=name, publicKey=public_key, privateKey=private_key
        )
        try:
            return self._create(payload)[0]
        except IndexError:
            return None


class CreateKeypairRequest(BaseModel):
    name: str
    publicKey: str
    privateKey: str
