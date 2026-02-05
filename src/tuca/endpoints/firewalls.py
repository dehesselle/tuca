# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from tuca.resource import Resource

from .endpoint import Endpoint


class Firewall(Resource):
    id: str
    name: str


class Firewalls(Endpoint[Firewall]):
    def __init__(self):
        super().__init__(Firewall, "firewalls")
        self.response_key = "values"
