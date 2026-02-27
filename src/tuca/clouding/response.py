# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from typing import Self

from pydantic import BaseModel, Field


class ResponseHeader(BaseModel):
    """
    The response header contains the available API `rate limits`_.

    .. _rate limits:
       https://api.clouding.io/docs/#section/Introduction/Rate-limit
    """

    rate_limit_limit: str = Field(alias="X-Rate-Limit-Limit", default="")
    rate_limit_remaining: str = Field(alias="X-Rate-Limit-Remaining", default="")
    rate_limit_reset: str = Field(alias="X-Rate-Limit-Reset", default="")


class Links(BaseModel):
    next: str | None
    previous: str | None


class Meta(BaseModel):
    total: int


class Pagination(BaseModel):
    links: Links = Field(default=Links(next=None, previous=None))
    meta: Meta = Field(default=Meta(total=0))

    @classmethod
    def new(
        cls, links: Links = Links(next=None, previous=None), meta: Meta = Meta(total=0)
    ) -> Self:
        return cls(links=links, meta=meta)
