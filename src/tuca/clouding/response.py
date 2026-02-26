# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from pydantic import BaseModel, Field


class ResponseHeader(BaseModel):
    rate_limit_limit: str = Field(alias="X-Rate-Limit-Limit", default="")
    rate_limit_remaining: str = Field(alias="X-Rate-Limit-Remaining", default="")
    rate_limit_reset: str = Field(alias="X-Rate-Limit-Reset", default="")


class ResponseLinks(BaseModel):
    next: str | None
    previous: str | None


class ResponseMeta(BaseModel):
    total: int
