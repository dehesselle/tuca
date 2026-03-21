# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from pydantic import Field

from .resource import SERIALIZE_ALWAYS, IdentifiableResource, NamedResource, Resource


class FirewallRule(IdentifiableResource):
    description: str
    enabled: bool
    portRangeMin: int | None
    portRangeMax: int | None
    protocol: str
    sourceIp: str


class AttachedPublicPort(IdentifiableResource):
    ipAddress: str
    macAddress: str


class AttachedVpcPort(IdentifiableResource):
    ipAddress: str
    macAddress: str
    vpcId: str


class FirewallAttachment(Resource):
    publicPorts: list[AttachedPublicPort]
    serverId: str
    serverName: str
    vpcPorts: list[AttachedVpcPort]


class Firewall(NamedResource):
    attachments: list[FirewallAttachment]
    description: str = Field(json_schema_extra=SERIALIZE_ALWAYS)
    rules: list[FirewallRule]
