# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from tuca.clouding import Clouding
from tuca.endpoints.flavors import Flavors
from tuca.endpoints.images import Images
from tuca.endpoints.volumes import Volumes


class Client(Clouding):
    """entry point for using tuca as a library

    The client does the HTTP work itself; its endpoints call back into it.
    """

    # TODO: inheriting from Clouding is temporary, it will be fully absorbed eventually

    def __init__(self, token: str):
        super().__init__(token)
        self.flavors = Flavors(self)
        self.images = Images(self)
        self.volumes = Volumes(self)
