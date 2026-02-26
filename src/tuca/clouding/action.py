from enum import StrEnum, auto
from typing import Self

from pydantic import BaseModel


class Status(StrEnum):
    """The current status of the action."""

    PENDING = auto()
    IN_PROGRESS = "inProgress"
    COMPLETED = auto()
    ERRORED = auto()


class Action(BaseModel):
    """
    For long-running actions, such as creating a server, the API returns an `Action`_
    object that provides information about the progress and outcome of the action.

    .. _Action:
       https://api.clouding.io/docs/#tag/Actions
    """

    id: str
    status: Status
    type: str
    startedAt: str
    completedAt: str | None
    resourceId: str
    resourceType: str

    @property
    def as_dict(self) -> dict:
        return {"actions": [self.model_dump()]}

    @classmethod
    def new(
        cls,
        id: str = "",
        status: Status = Status.ERRORED,
        type: str = "",
        startedAt: str = "",
        completedAt: str | None = None,
        resourceId="",
        resourceType="",
    ) -> Self:
        return cls(
            id=id,
            status=status,
            type=type,
            startedAt=startedAt,
            completedAt=completedAt,
            resourceId=resourceId,
            resourceType=resourceType,
        )
