# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .resource import Resource


class VolumeSize(Resource):
    storageType: str
    sizeGb: int
    pricePerHour: float
    pricePerMonthApprox: float
