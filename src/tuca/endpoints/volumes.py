# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from tuca.resources.volumesize import VolumeSize

from .endpoint import Endpoint

if TYPE_CHECKING:
    from tuca.client import Client


class Volumes(Endpoint[VolumeSize]):
    """volume `sizes`_

    .. _sizes:
      https://api.clouding.io/docs/#tag/Sizes/operation/ListAllVolumeSizes
    """

    def __init__(self, client: Client):
        super().__init__(VolumeSize, "sizes/volumes", client)
        self.response_key = "volumeSizes"

    @property
    def all(self) -> list[int]:
        self.get()
        return [volumesize.sizeGb for volumesize in self.resources]
