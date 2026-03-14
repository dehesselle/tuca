# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .image import Image
from .resource import NamedResource


class Snapshot(NamedResource):
    createdAt: str
    sizeGb: int
    image: Image
