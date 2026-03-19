# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .actions import setup_actions_endpoint
from .firewalls import setup_firewalls_endpoint
from .flavors import setup_flavors_endpoint
from .images import setup_images_endpoint
from .keypairs import setup_keypairs_endpoint
from .servers import setup_servers_endpoint
from .snapshots import setup_snapshots_endpoint
from .volumes import setup_volumes_endpoint
