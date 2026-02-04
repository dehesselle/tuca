# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import json

from pydantic import BaseModel


class Resource(BaseModel):
    pass

    @property
    def as_str(self):
        return json.dumps(
            self.model_dump(),
            indent=4,
            sort_keys=True,
        )
