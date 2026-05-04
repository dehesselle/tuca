# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from enum import StrEnum, auto

from pydantic import Field

from .resource import SERIALIZE_ALWAYS, IdentifiableResource


class Status(StrEnum):
    """The current status of the action."""

    COMPLETED = auto()
    ERRORED = auto()
    IN_PROGRESS = "inProgress"
    PENDING = auto()


class Action(IdentifiableResource):
    """
    For long-running actions, such as creating a server, the API returns an `Action`_
    object that provides information about the progress and outcome of the action.

    .. _Action:
       https://api.clouding.io/docs/#tag/Actions
    """

    completedAt: str | None = Field(json_schema_extra=SERIALIZE_ALWAYS)
    resourceId: str = Field(json_schema_extra=SERIALIZE_ALWAYS)
    resourceType: str = Field(json_schema_extra=SERIALIZE_ALWAYS)
    startedAt: str = Field(json_schema_extra=SERIALIZE_ALWAYS)
    status: Status = Field(json_schema_extra=SERIALIZE_ALWAYS)
    type: str = Field(json_schema_extra=SERIALIZE_ALWAYS)
