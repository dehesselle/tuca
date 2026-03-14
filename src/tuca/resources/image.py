# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from pydantic import BaseModel, Field

from .resource import NamedResource


class AccessMethods(BaseModel):
    sshKey: str
    password: str


class Image(NamedResource):
    accessMethods: AccessMethods
    minimumSizeGb: int = Field(default=0)  # default for reusability in Snapshot
