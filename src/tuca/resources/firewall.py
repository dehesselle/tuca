# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from pydantic import Field

from .resource import SERIALIZE_ALWAYS, IdentifiableResource, NamedResource, Resource


class FirewallRule(IdentifiableResource):
    description: str
    protocol: str
    portRangeMin: int | None
    portRangeMax: int | None
    sourceIp: str
    enabled: bool


class AttachedPublicPort(IdentifiableResource):
    ipAddress: str
    macAddress: str


class AttachedVpcPort(IdentifiableResource):
    ipAddress: str
    macAddress: str
    vpcId: str


class FirewallAttachment(Resource):
    serverId: str
    serverName: str
    publicPorts: list[AttachedPublicPort]
    vpcPorts: list[AttachedVpcPort]


class Firewall(NamedResource):
    description: str = Field(json_schema_extra=SERIALIZE_ALWAYS)
    rules: list[FirewallRule]
    attachments: list[FirewallAttachment]
