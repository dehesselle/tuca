# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from enum import StrEnum, auto

from .resource import IdentifiableResource


class Status(StrEnum):
    """The current status of the action."""

    PENDING = auto()
    IN_PROGRESS = "inProgress"
    COMPLETED = auto()
    ERRORED = auto()


class Action(IdentifiableResource):
    """
    For long-running actions, such as creating a server, the API returns an `Action`_
    object that provides information about the progress and outcome of the action.

    .. _Action:
       https://api.clouding.io/docs/#tag/Actions
    """

    status: Status
    type: str
    startedAt: str
    completedAt: str | None
    resourceId: str
    resourceType: str

    @property
    def as_dict(self) -> dict:
        return {"actions": [self.model_dump()]}
