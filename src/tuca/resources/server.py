# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from pydantic.experimental.missing_sentinel import (
    MISSING,  # https://docs.pydantic.dev/dev/concepts/experimental/#missing-sentinel
)

from .action import Action
from .resource import NamedResource


class Server(NamedResource):
    createdAt: str = ""
    publicIp: str | None = ""
    status: str
    action: Action | MISSING = MISSING
