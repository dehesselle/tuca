# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from pydantic import BaseModel, Field

from .resource import SERIALIZE_ALWAYS, NamedResource


class AccessMethods(BaseModel):
    sshKey: str
    password: str


class Image(NamedResource):
    accessMethods: AccessMethods = Field(json_schema_extra=SERIALIZE_ALWAYS)
    billingUnit: str | None
    minimumSizeGb: int = Field(json_schema_extra=SERIALIZE_ALWAYS)
    pricePerHour: float
    pricePerMonthApprox: float
