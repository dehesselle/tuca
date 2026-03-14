# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .resource import IdentifiableResource


class Flavor(IdentifiableResource):
    vCores: float
    ramGb: int
    pricePerHour: float
    pricePerMonthApprox: float
