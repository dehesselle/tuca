# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import json

from pydantic import BaseModel, Field
from pydantic.config import JsonDict

SERIALIZE_ALWAYS_KEY = "serialize_always"
SERIALIZE_ALWAYS: JsonDict = {SERIALIZE_ALWAYS_KEY: True}


class Resource(BaseModel):
    """generalized base class for all resources"""

    @property
    def as_str(self):
        return json.dumps(
            self.model_dump(),
            indent=4,
            sort_keys=True,
        )

    @classmethod
    def get_marked_fields(cls, key: str) -> set[str]:
        result = set()

        for field_name, field_info in cls.model_fields.items():
            extra = field_info.json_schema_extra
            if type(extra) is dict and not callable(extra):  # for Pyright
                if key in extra.keys():
                    result.add(field_name)

        return result


class IdentifiableResource(Resource):
    """base for resources with `id` property"""

    id: str = Field(json_schema_extra=SERIALIZE_ALWAYS)


class NamedResource(IdentifiableResource):
    """base for resources with `id` and `name` properties"""

    name: str = Field(json_schema_extra=SERIALIZE_ALWAYS)
