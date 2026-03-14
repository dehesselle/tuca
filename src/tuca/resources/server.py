# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from enum import StrEnum

from pydantic.experimental.missing_sentinel import (
    MISSING,  # https://docs.pydantic.dev/dev/concepts/experimental/#missing-sentinel
)

from .action import Action
from .resource import NamedResource


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


class Server(NamedResource):
    createdAt: str = ""
    publicIp: str | None = ""
    status: Status
    action: Action | MISSING = MISSING
