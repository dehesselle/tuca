# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from enum import StrEnum

from pydantic import Field

from .resource import SERIALIZE_ALWAYS, NamedResource, Resource


class SshKey(StrEnum):
    NOT_SUPPORTED = "not-supported"
    OPTIONAL = "optional"
    REQUIRED = "required"
    REQUIRED_WITH_PRIVATE_KEY = "required-with-private-key"


class Password(StrEnum):
    NOT_SUPPORTED = "not-supported"
    OPTIONAL = "optional"
    REQUIRED = "required"


class RestoreServerAccessMethods(Resource):
    password: Password
    sshKey: SshKey


class SnapshotImageInfo(NamedResource):
    accessMethods: RestoreServerAccessMethods


class SnapshotCost(Resource):
    pricePerHour: float
    pricePerMonthApprox: float


class Snapshot(NamedResource):
    cost: SnapshotCost
    createdAt: str = Field(json_schema_extra=SERIALIZE_ALWAYS)
    description: str | None
    image: SnapshotImageInfo = Field(json_schema_extra=SERIALIZE_ALWAYS)
    sizeGb: int = Field(json_schema_extra=SERIALIZE_ALWAYS)
    sourceServerName: str
