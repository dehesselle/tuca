# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from enum import StrEnum

from pydantic import Field
from pydantic.experimental.missing_sentinel import (
    MISSING,  # https://docs.pydantic.dev/dev/concepts/experimental/#missing-sentinel
)

from .action import Action
from .resource import SERIALIZE_ALWAYS, IdentifiableResource, NamedResource


class Status(StrEnum):
    """The current status of the server.

    Enumeration as in `ListAllServers`_.

    .. _ListAllServers:
       https://api.clouding.io/docs/#tag/Servers/operation/ListAllServers
    """

    ACTIVE = "Active"
    ARCHIVED = "Archived"
    ARCHIVING = "Archiving"
    CREATING = "Creating"
    DELETED = "Deleted"
    DELETING = "Deleting"
    ERROR = "Error"
    PENDING = "Pending"
    REBOOTING = "Rebooting"
    RESTORING_BACKUP = "RestoringBackup"
    RESETTING_PASSWORD = "ResettingPassword"
    RESTORING_SNAPSHOT = "RestoringSnapshot"
    RESIZE = "Resize"
    STARTING = "Starting"
    STOPPED = "Stopped"
    STOPPING = "Stopping"
    UNARCHIVING = "Unarchiving"
    UNKNOWN = "Unknown"


class ServerImageInfo(NamedResource):
    pass


class PowerState(StrEnum):
    CRASHED = "Crashed"
    NO_STATE = "NoState"
    PAUSED = "Paused"
    RUNNING = "Running"
    SHUTDOWN = "Shutdown"
    SUSPENDED = "Suspended"


class PublicPortDescriptor(IdentifiableResource):
    ipAddress: str
    macAddress: str


class VpcDescriptor(NamedResource):
    pass


class VpcPortDescriptor(IdentifiableResource):
    ipAddress: str
    macAddress: str
    vpc: VpcDescriptor


class Server(NamedResource):
    action: Action | MISSING = Field(
        default=MISSING, json_schema_extra=SERIALIZE_ALWAYS
    )
    createdAt: str = Field(default="", json_schema_extra=SERIALIZE_ALWAYS)
    dnsAddress: str | None = None
    features: list[str] = []
    flavor: str
    hostname: str
    image: ServerImageInfo
    powerState: PowerState = Field(default=PowerState.NO_STATE)
    publicPorts: list[PublicPortDescriptor] = Field(
        default=[], json_schema_extra=SERIALIZE_ALWAYS
    )
    ramGb: int
    sshKeyId: str | None = None
    status: Status = Field(json_schema_extra=SERIALIZE_ALWAYS)
    vCores: float
    volumeSizeGb: int
    vpcPorts: list[VpcPortDescriptor] = []
