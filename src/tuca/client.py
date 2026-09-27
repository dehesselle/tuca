# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from tuca.clouding import Clouding
from tuca.endpoints.actions import Actions
from tuca.endpoints.firewalls import Firewalls
from tuca.endpoints.flavors import Flavors
from tuca.endpoints.images import Images
from tuca.endpoints.keypairs import Keypairs
from tuca.endpoints.servers import Servers
from tuca.endpoints.snapshots import Snapshots
from tuca.endpoints.volumes import Volumes


class Client(Clouding):
    """entry point for using tuca as a library

    The client does the HTTP work itself; its endpoints call back into it.
    """

    # TODO: inheriting from Clouding is temporary, it will be fully absorbed eventually

    def __init__(self, token: str):
        super().__init__(token)
        self.actions = Actions(self)
        self.firewalls = Firewalls(self)
        self.flavors = Flavors(self)
        self.images = Images(self)
        self.keypairs = Keypairs(self)
        self.servers = Servers(self)
        self.snapshots = Snapshots(self)
        self.volumes = Volumes(self)
